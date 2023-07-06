
import json

from layers.common.python.services.transcript_storage_service import TranscriptStorageService
from analyse_transcript_helper import AnalyseTrascriptHelper


def main():
    with open('~/Downloads/transcript.json', 'r') as f:
        data = json.reads(f.read())

    ts = TranscriptStorageService('CallAnalysisStackDev-sedricanalysisrequestsDEED6420-1LY8XA7DAE3ZR')
    analysis_helper = AnalyseTrascriptHelper()
    analysis_helper.analyse_transcript(data, ts)


if __name__ == '__main__':
    main()
