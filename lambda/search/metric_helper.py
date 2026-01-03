import boto3
import json
import time
from datetime import datetime

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch')


def put_metric(name, value, unit='None', dimensions=None):
    """Send a custom metric to CloudWatch"""
    try:
        metric_data = {
            'MetricName': name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow()
        }
        if dimensions:
            metric_data['Dimensions'] = dimensions

        cloudwatch.put_metric_data(
            Namespace='DevDocBot',
            MetricData=[metric_data]
        )
    except Exception as e:
        print(f"Failed to push metric {name}: {e}")


def log_structured(event_type, details, level='INFO'):
    """Print a JSON log for CloudWatch Insights"""
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'level': level,
        **details
    }
    print(json.dumps(entry))