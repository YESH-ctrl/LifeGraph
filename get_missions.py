import sys, os, boto3, json
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def get_missions():
    table = GraphRepository().table
    kwargs = {}
    missions = []
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for i in res.get('Items', []):
            if i['PK'].startswith('MISSION#'):
                missions.append(i['missionId'])
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    with open('missions.txt', 'w') as f:
        f.write('\n'.join(missions))
        
if __name__ == '__main__':
    get_missions()
