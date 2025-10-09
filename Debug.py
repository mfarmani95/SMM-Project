import logging
import sys
from pathlib import Path

# Optional: let you run the repo without pip install
# (uncomment if you're working in dev mode)
# sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from smm.main import SMM  # or whatever your main entry function is

def setup_logger():
    """Configure logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,  # use INFO if you want less verbosity
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("debug.log", mode="w")
        ]
    )
    logging.getLogger().info("Logger initialized")

if __name__ == "__main__":
    setup_logger()
    
    # Point to a sample YAML config
    config_path = Path("/Users/mohammad/Desktop/PHD/PHD/Behrangi  and Niu/ISMN/SMM_code/smm/configs/Test.yml")
    if not config_path.exists():
        logging.error(f"Config file not found: {config_path}")
        sys.exit(1)

    logging.info(f"Starting SMM analysis using config: {config_path}")

    SMM(config_path)
       
   

