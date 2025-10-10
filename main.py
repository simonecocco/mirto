from controllers.flux_control import start_queue
from controllers.rest_api import start_rest_api
from utils.logger_utils import setup_logger
from user.user_preferences import UserPreferences
from mirto.utils.process_orchestrator import ProcessOrchestrator
from mirto.utils.process_synchronizer import ProcessSynchronizer


def main(user_preferences, logger):
    logger = setup_logger()

    user_preferences = UserPreferences()

    process_synchronizer = ProcessSynchronizer()
    process_orchestrator = ProcessOrchestrator(
        process_synchronizer,
        user_preferences,
        logger,
    )

    try:
        process_orchestrator.new_process('API', start_rest_api)
        process_orchestrator.new_process('Queue', start_queue)
    except KeyboardInterrupt:
        del process_orchestrator

    logger.info("Mirto stopped")


if __name__ == '__main__':
    main()
