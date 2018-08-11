#!/usr/bin/python
"""
A demo exercising testpool behavior. Read the quick start guide in
order to configure Testpool server and then come back to this script.

This demo supports both the fake and docker products. Fake is a good
tool for seeing behavior and development without having to setup additional
tools. The docker product requires install docker locally in order to
see the demo in action. Check the dashboard to see the status of the various
pool of resources at:

  http://127.0.0.1:8000/testpool/view/dashboard
"""
import sys
import random
import time
import argparse
import logging
import requests


class Rest(object):
    """ Example calling REST interface. """

    # pylint: disable=too-many-arguments

    def __init__(self, hostname):
        fmt = "http://%s:8000/testpool/api/v1/"
        self.url = fmt % hostname

    def profile_add(self, name, connection, product, template_name,
                    resource_max):
        """ Add a profile. """

        params = {
            "connection": connection,
            "product": product,
            "resource_max": resource_max,
            "template_name": template_name
        }
        url = self.url + "profile/add/%s" % name
        rtc = requests.post(url, params=params)
        rtc.raise_for_status()
        return rtc

    def profile_remove(self, name, immediate=False):
        """ Remove a profile. """
        fmt = self.url + "profile/remove/%s?immediate=%s"
        url = fmt % (name, immediate)
        rtc = requests.delete(url)
        rtc.raise_for_status()
        return rtc

    def acquire(self, profile):
        """ Acquire a resource. """
        url = self.url + "profile/acquire/%s" % profile
        return requests.get(url)

    def release(self, rsrc):
        """ Release a resource. """
        url = self.url + "profile/release/%s" % rsrc
        return requests.get(url)


FAKE_PROFILE_NAMES = ["ubuntu16.04", "centos7.0", "vmware", "ESX6.5"]
DOCKER_PROFILE_NAMES = ["nginx"]


def add_profiles(rest, args):
    """ Create all of the profiles. """

    if args.product == "fake":
        resource_maxes = [10, 40, 100, 50]
        for (name, resource_max) in zip(FAKE_PROFILE_NAMES, resource_maxes):
            template_name = "template_name.%s" % name
            logging.info("adding profile %s", name)
            rest.profile_add(name, "localhost", args.product, template_name,
                             resource_max)
        return FAKE_PROFILE_NAMES
    elif args.product == "docker":
        resource_maxes = [10]
        template_name = "nginx:latest"
        for (name, resource_max) in zip(DOCKER_PROFILE_NAMES, resource_maxes):
            logging.info("adding profile %s", name)
            rest.profile_add(name, "localhost", args.product, template_name,
                             resource_max)
        return DOCKER_PROFILE_NAMES
    else:
        raise ValueError("unsupported product %s" % args.product)


def remove_profiles(rest):
    """ Create all of the profiles. """

    for name in FAKE_PROFILE_NAMES + DOCKER_PROFILE_NAMES:
        try:
            logging.info("remove profile %s", name)
            rest.profile_remove(name, immediate=True)
        except Exception as arg:  # pylint: disable=broad-except
            logging.info(arg)


class State(object):
    """ Track demo action. """

    ACTIVE = 0
    RELEASE = 1
    WAIT = 2

    def __init__(self):
        self.stages = [60, 30, 30]
        self._stage = State.ACTIVE
        self._count = 0

    def count(self):
        """ Return count. """

        return self._count

    def next(self):
        """ Return the next stage. """

        self._count += 1
        if self._count >= self.stages[self._stage]:
            self._stage += 1
            self._stage %= len(self.stages)
        return self._stage


def do_start(args):
    """ Start demo.

    The demo will randomally acquire resources. Then after 60 seconds, free
    all resources, wait 30 seconds and then go back to acquiring resources.
    """

    actions = ["release", "acquire"]

    rest = Rest(args.hostname)
    acquired_resources = []

    remove_profiles(rest)
    if args.cleanup:
        return 0
    profile_names = add_profiles(rest, args)
    count = 0

    state = State()

    while args.count == -1 or count < args.count:
        value = state.next()
        if value == State.ACTIVE:
            logging.info("acquire and releasing resources")
            action = random.choice(actions)
            profile = random.choice(profile_names)
            if action == "acquire":
                logging.info("acquire %s", profile)
                resp = rest.acquire(profile)
                if resp.status_code == 200:
                    rsrc = resp.json()
                    acquired_resources.append(rsrc)
                    logging.info("acquired %s:%s", profile, rsrc)
                else:
                    logging.info("%s: %s", resp.status_code,
                                 resp.json()["msg"])
            elif action == "release" and acquired_resources:
                logging.info("release %s", profile)
                index = random.randrange(0, len(acquired_resources))
                rest.release(rsrc)
                del acquired_resources[index]
                logging.info("released %s:%s", profile, rsrc)
        elif value == State.RELEASE and state.count() == 0:
            logging.info("releasing all resources")
            while acquired_resources:
                rsrc = acquired_resources.pop()
                rest.release(rsrc)
        elif value == State.WAIT and state.count() == 0:
            logging.info("sleeping")
        time.sleep(1)
    return 0


def args_process(args):
    """ Process any generic parameters. """

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
        logging.info("verbosity level set to INFO")
    elif args.verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
        logging.info("verbosity level set to DEBUG")


def argparser(progname):
    """ Create top level argument parser. """

    arg_parser = argparse.ArgumentParser(prog=progname, description=__doc__)
    arg_parser.add_argument('--count', required=False, default=-1, type=int,
                            help="How many seconds to run the demo.")
    arg_parser.add_argument('--verbose', '-v', required=False, action="count",
                            help="enable debug verbosity.")
    arg_parser.add_argument('--hostname', default="127.0.0.1",
                            help="Location of the testpool daemon")
    arg_parser.add_argument('--product', default="fake",
                            help="Product used for the demo")
    arg_parser.add_argument('--cleanup', default=False, action="store_true",
                            help="Remove all demo profiles")
    return arg_parser


def main():
    """ Entry point. """
    parser = argparser("demo")
    args = parser.parse_args()
    args_process(args)
    return do_start(args)


if __name__ == "__main__":
    try:
        main()
    except Exception, arg:  # pylint: disable=broad-except
        logging.exception(arg)
        sys.exit(1)
