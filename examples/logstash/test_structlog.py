#!/usr/bin/python
"""
Store structured content to a log.
"""
import time
import logging
import random
import structlog

ROOT_LOGGER = logging.getLogger()
HANDLER = logging.FileHandler("/var/log/testpool/logstash.log")
ROOT_LOGGER.addHandler(HANDLER)
ROOT_LOGGER.setLevel(logging.INFO)


def main():
    """ Push content to the structure logging. """

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            # structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S",
            # structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S",
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    print "starting loop"

    log = structlog.wrap_logger(ROOT_LOGGER)
    log.info(profile="test.example.1", vm_count=10, vm_max=10)
    log.info(profile="test.example.2", vm_count=10, vm_max=10)

    count1 = 10
    count2 = 10
    for _ in range(10000):
        if random.randint(0, 1) == 0:
            count1 -= 1
        else:
            count1 += 1
        count1 = max(count1, 0)
        count1 = min(count1, 10)
        log.info(profile="test.example.1", vm_count=count1, vm_max=10)

        if random.randint(0, 1) == 0:
            count2 -= 1
        else:
            count2 += 1

        count2 = max(count2, 0)
        count2 = min(count2, 10)

        log.info(profile="test.example.2", vm_count=count2, vm_max=10)
        seconds = random.randint(0, 30)
        print "test.example.1", count1, "test.example.2", count2
        time.sleep(seconds)

main()
