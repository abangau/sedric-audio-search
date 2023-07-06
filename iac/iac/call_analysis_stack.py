from os import environ, write
import os
from typing import Mapping
from aws_cdk import (
    Duration,
    Stack,
    aws_apigateway as gw,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_dynamodb as ddb,
    aws_lambda,
    aws_lambda_event_sources
)
from constructs import Construct
from iac.utils import add_tags


class CallAnalysisStack(Stack):

    def __init__(self, scope: Construct, app_config: dict, **kwargs) -> None:
        super().__init__(scope, app_config['app_name'], **kwargs)


        # Resources first
        self.queues = self._create_queues(app_config.get('sqs', {}))
        self.buckets = self._create_buckets(app_config.get('s3', {}))
        self.dbs = self._create_dynamo_tables(app_config.get('dynamo', {}))

        # Functions after
        self.layers = self._create_lambda_layers(app_config.get('lambda', {}).get('layers', {}))
        self.functions = self._create_lambda_functions(app_config.get('lambda', {}).get('functions', {}))

        # Rest API last
        self.api_gateways = self._create_api_gateways(app_config.get('api_gateways', {}))

        # For compliance with policies of account I am using
        for construct in Stack.of(self).node.find_all():
            add_tags(construct)


    def _create_queues(self, queues: dict) -> Mapping[str, sqs.Queue]:
        queues_created: Mapping[str, sqs.Queue] = {}
        for queue_name, queue_config in queues.items():
            queue = sqs.Queue(
                self, queue_name,
                visibility_timeout=Duration.seconds(queue_config.get('visibility_timeout', 300))
            )
            queues_created[queue_name] = queue

        return queues_created

    def _create_buckets(self, buckets: dict) -> Mapping[str, s3.Bucket]:
        buckets_created: Mapping[str, s3.Bucket] = {}
        for bucket_name, bucket_config in buckets.items():
            bucket =  s3.Bucket(
                self, bucket_name,
                bucket_name=bucket_name,
            )
            buckets_created[bucket_name] = bucket

        return buckets_created

    def _create_dynamo_tables(self, tables: dict) -> Mapping[str, ddb.Table]:
        dbs_created: Mapping[str, ddb.Table] = {}
        for table_name, table_config in tables.items():
            db = ddb.Table(
                self, table_name,
                partition_key=ddb.Attribute(name=table_config['partition_key'], type=ddb.AttributeType.STRING),
                read_capacity=table_config.get('read_capacity', 5),
                write_capacity=table_config.get('write_capacity', 3),
            )
            dbs_created[table_name] = db

        return dbs_created

    def _create_lambda_layers(self, layers: dict) -> Mapping[str, aws_lambda.LayerVersion]:
        stack_layers: Mapping[str, aws_lambda.LayerVersion] = {}
        for layer_name, layer_config in layers.items():
            if 'path' in layer_config:
                new_layer = aws_lambda.LayerVersion(
                    self,
                    layer_name,
                    layer_version_name=layer_name,
                    code=aws_lambda.Code.from_asset(
                        layer_config.get('path', '').format(
                            PROJECT_ROOT=os.environ.get('PROJECT_ROOT')
                        )
                    ),
                    compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_10],
                    compatible_architectures=[aws_lambda.Architecture.ARM_64]
                )
            elif 'arn' in layer_config:
                new_layer = aws_lambda.LayerVersion.from_layer_version_arn(
                        self,
                        layer_name,
                        layer_config.get('arn')
                    )
            stack_layers[layer_name] = new_layer

        return stack_layers

    def _get_resource_reference(self, resource_name, resource_type, get_arn=True, add_wildcard=True):
        if resource_type == 'dynamo':
            return [self.dbs[resource_name].table_arn if get_arn else self.dbs[resource_name].table_name]
        elif resource_type == 's3':
            bucket_ref = self.buckets[resource_name].bucket_arn if get_arn else self.buckets[resource_name].bucket_name
            if add_wildcard:
                return [bucket_ref, f'{bucket_ref}/*']
            return [bucket_ref]
        elif resource_type == 'sqs':
            return [self.queues[resource_name].queue_arn if get_arn else self.queues[resource_name].queue_name]

    def _create_api_gateways(self, api_gateways: dict) -> Mapping[str, gw.RestApi]:
        gateways: Mapping[str, gw.RestApi] = {}
        for name, config in api_gateways.items():
            api: gw.RestApi = gw.RestApi(
                self,
                name,
                description=config.get('description'),
                cloud_watch_role=False
            )
            for _, resource_config in config.get('resources', {}).items():
                resource = api.root.add_resource(
                    resource_config.get('path')
                )
                for method in resource_config.get('methods', []):
                    resource.add_method(
                        method, gw.LambdaIntegration(
                            self.functions[resource_config.get('function')]
                        )
                    )
            gateways[name] = api
        return gateways

    def _create_lambda_functions(self, functions: dict) -> Mapping[str, aws_lambda.Function]:
        lambdas: Mapping[str, aws_lambda.Function] = {}
        for name, config in functions.items():

            # Solve environment variables for lambdas
            env_vars = {}
            for obj_type, env_vars_config in config.get('env_vars', {}).items():
                if obj_type == 'dynamo':
                    for env_var_name, env_var_table_reference in env_vars_config.items():
                        env_vars[env_var_name] = self.dbs.get(env_var_table_reference).table_name
                elif obj_type == 's3':
                    for env_var_name, env_var_bucket_reference in env_vars_config.items():
                        env_vars[env_var_name] = self.buckets.get(env_var_bucket_reference).bucket_name
                elif obj_type == 'sqs':
                    for env_var_name, env_var_queue_reference in env_vars_config.items():
                        env_vars[env_var_name] = self.queues.get(env_var_queue_reference).queue_name

            # Create function
            new_function: aws_lambda.Function = aws_lambda.Function(
                self,
                name,
                function_name=name,
                code=aws_lambda.Code.from_asset(config.get('path').format(
                    PROJECT_ROOT=os.environ.get('PROJECT_ROOT')
                )),
                runtime=aws_lambda.Runtime.PYTHON_3_10,
                layers=[self.layers.get(lname) for lname in config.get('layers', [])],
                handler=config.get('handler'),
                memory_size=config.get('memory', 128),
                timeout=Duration.seconds(config.get('timeout', 300)),
                environment=env_vars,
                reserved_concurrent_executions=config.get('concurrency'),
                architecture=aws_lambda.Architecture.ARM_64
            )

            # Function triggers next
            for _, trigger_config in config.get('triggers', {}).items():
                trigger_type = trigger_config.get('type')
                trigger_construct = trigger_config.get('ref')

                if trigger_type == 'sqs':
                    new_function.add_event_source(
                        aws_lambda_event_sources.SqsEventSource(
                            self.queues[trigger_construct],
                            batch_size=5
                        )
                    )
                elif trigger_type == 's3':
                    filters_handler =  s3.NotificationKeyFilter(
                        prefix=trigger_config.get('prefix', ''),
                        suffix=trigger_config.get('suffix', '')
                    )
                    self.buckets[trigger_construct].add_event_notification(
                        s3.EventType.OBJECT_CREATED,
                        s3n.LambdaDestination(new_function),
                        filters_handler
                    )

            # Finally, policies
            if config.get('allow_transcribe_job'):
                new_function.add_to_role_policy(
                    iam.PolicyStatement(
                        effect=iam.Effect(effect),
                        resources=['*'],  # ideally add a proper wildcard here at some point
                        actions=['transcribe:StartTranscriptionJob']
                    )
                )

            for resource_type, policy_config in config.get('policies', {}).items():
                for resource_reference, effect_groups in policy_config.items():
                    for effect, actions in effect_groups.items():
                        new_function.add_to_role_policy(
                            iam.PolicyStatement(
                                effect=iam.Effect(effect),
                                resources=self._get_resource_reference(resource_reference, resource_type, True),
                                actions=actions
                            )
                        )

            # Add the lambda to our list
            lambdas[name] = new_function

        return lambdas
