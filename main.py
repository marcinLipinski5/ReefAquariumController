import logging


class ReefAquariumController:

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("aquarium_log.log"),
                logging.StreamHandler()
            ]
        )
