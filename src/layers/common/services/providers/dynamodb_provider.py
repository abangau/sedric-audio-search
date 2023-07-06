import boto3


class DynamoDBProvider(object):
    """
    This is a singleton-ish class. The scope of it is to have only one shared connection
    to a table (can have multiple connections to different tables).
    """
    __instance = {}

    @staticmethod
    def get_instance(table_name: str):
        """
        Returns the an instance of the singleton with the table opened and ready
        """
        if DynamoDBProvider.__instance.get(table_name) is None:
            DynamoDBProvider(table_name)

        return DynamoDBProvider.__instance.get(table_name)

    def __init__(self, table_name):
        if DynamoDBProvider.__instance.get(table_name) is not None:
            raise Exception("Please use getInstance instead!")

        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        DynamoDBProvider.__instance[table_name] = self
