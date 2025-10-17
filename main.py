from sys import exit
from controllers.flux_control import start_queue
from controllers.rest_api import start_rest_api
from utils.logger_utils import setup_logger
from utils.system_checker import SystemChecker
from user.user_preferences import UserPreferences
from utils.process_orchestrator import ProcessOrchestrator
from utils.process_synchronizer import ProcessSynchronizer


def main():
    logger = setup_logger('Mirto')
    if not SystemChecker.has_sudo_permissions():
        logger.critical('Permission error! Exiting')
        exit(1)

    user_preferences = UserPreferences()

    process_synchronizer = ProcessSynchronizer()
    process_orchestrator = ProcessOrchestrator(
        process_synchronizer,
        user_preferences,
        logger,
    )

    try:
        process_orchestrator.new_process('API', start_rest_api)
        #process_orchestrator.new_process('Queue', start_queue)

        while True:
            continue
    except KeyboardInterrupt:
        del process_orchestrator

    logger.info("Mirto stopped")


if __name__ == '__main__':
    main()
