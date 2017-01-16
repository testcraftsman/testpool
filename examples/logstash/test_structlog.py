import sys
import logging
import structlog

root_logger = logging.getLogger()

#handler = logging.StreamHandler(sys.stdout)
#root_logger.addHandler(handler)

handler = logging.FileHandler("/var/log/testpool/logstash.log")
root_logger.addHandler(handler)

root_logger.setLevel(logging.INFO)


structlog.configure(
          processors=[
              structlog.stdlib.filter_by_level,
              structlog.stdlib.add_log_level,
              structlog.stdlib.PositionalArgumentsFormatter(),
              # structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S",
              #structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S",
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
log = structlog.wrap_logger(root_logger)
#PrintLogger())
for count in range(10000):
    log.info(profile="test.example", vm_count=count % 11, vm_max=10)
