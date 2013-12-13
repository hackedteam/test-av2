__author__ = 'fabrizio'

from AVCommon.logger import logging

from AVAgent import build
import AVAgent



def on_init(protocol, args):
    """ server side """
    return True


def on_answer(vm, success, answer):
    """ server side """
    pass


def execute(vm, args):
    #TODO
    # close instance
    (target_id, factory_id, ident, operation, target, factory) = build.connection.rcs

    # find scout process
    # kill process
    # delete file

    pass