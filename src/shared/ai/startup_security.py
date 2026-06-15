import os
import logging
import boto3

logger = logging.getLogger(__name__)

def run_startup_security_checks() -> bool:
    """
    Performs startup verification checks on AWS credentials and configs.
    Ensures safe operations.
    """
    logger.info("Executing Amazon Outcome Intelligence Startup Security Checks...")
    
    # 1. AWS Region validation
    region = os.environ.get("AWS_REGION")
    if not region:
        logger.warning("SECURITY CHECK WARNING: AWS_REGION environment variable is not explicitly set. Falling back to boto3 default config.")
    else:
        logger.info(f"Startup Security Check: AWS_REGION is set to '{region}'.")
        
    # 2. Check credentials profiles
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            logger.info("Startup Security Check: AWS credentials loaded successfully.")
            # Print masked access key for verification
            access_key = credentials.access_key
            if access_key:
                masked = access_key[:4] + "*" * (len(access_key) - 8) + access_key[-4:]
                logger.info(f"Using AWS Access Key ID: {masked}")
        else:
            logger.warning("SECURITY CHECK WARNING: No AWS credentials detected in environment. Application will run in Local Simulation Mode.")
    except Exception as e:
        logger.error(f"Startup Security Check Error: {e}. Defaulting to Local Simulation Mode.")
        
    logger.info("Startup Security Checks completed.")
    return True
