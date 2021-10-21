import logging


def get_logger(name, debug=False, info=True):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.captureWarnings(True)
    logger.setLevel(logging.WARNING)
    if info:
        logger.setLevel(logging.INFO)
    if debug:
        logger.setLevel(logging.DEBUG)
    return logger


_LOGGER = get_logger(__name__)


def y_n_input(prompt):
    answer = None
    invalid_prefix = ''
    while not answer:
        input_prompt = f"{invalid_prefix}{prompt} (y/n):"
        _LOGGER.debug(f"Prompting the user: '{input_prompt}'")
        validity_unverified = input(input_prompt)
        _LOGGER.debug(f"User response: '{validity_unverified}'")
        if validity_unverified in ['y', 'Y', 'n', 'N']:
            if validity_unverified in ['y', 'Y']:
                return True
            else:
                return False
        else:
            _LOGGER.warn('User response invalid')
            invalid_prefix = 'Invalid response. '
