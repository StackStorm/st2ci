import os

from st2common.runners.base_action import Action

from st2client.client import Client

ACTION_REF = 'st2ci.st2_pkg_e2e_test'


class CancelOldBuildsForPrAction(Action):
    def run(self, build_num, pr_num):
        if not build_num or not pr_num:
            self.logger.info('Skipping old build cancelation because pr num or build num is not '
                             'set')
            return

        build_num = int(build_num)
        pr_num = int(pr_num)

        # 1. Find any matching executions
        client = self._get_client()

        execution_apis = client.liveactions.query(action=ACTION_REF, status='running', limit=100,
                                                  include_attributes='id,status,parameters')

        to_cancel_execution_apis = self._filter_executions(execution_apis,
                                                           current_build_num=build_num,
                                                           current_pr_num=pr_num)

        to_cancel_execution_apis = execution_apis
        self.logger.info('Found "%s" old execution(s) for PR "%s" to be canceled' %
                         (len(to_cancel_execution_apis), pr_num))
        # Make sure we exclude current one and not cancel the current / latest one

        # 2. Cancel old ones
        for execution_api in to_cancel_execution_apis:
            msg = ('Canceling old execution with id "%s" for PR "%s" (build_num %s < '
                   'current_build_num %s)' % (execution_api.id, pr_num,
                                              execution_api.parameters['pr_num'], pr_num))
            self.logger.info(msg)
            client.liveactions.delete_by_id(execution_api.id)

            # TODO: We should probably also ensure here that cleanup task is also called..

    def _filter_executions(self, execution_apis, current_build_num, current_pr_num):
        # Filter the executions and only return old ones
        result = []

        for execution_api in execution_apis:
            parameters = execution_api.parameters

            build_num = int(parameters.get('build_num', 0))
            pr_num = int(parameters.get('pr_num', 0))

            # Additional safety check to make sure we don't cancel current build
            if build_num == current_build_num:
                continue

            # Skip executions for other PRs
            # Builds without pr_num set are not triggered as part of a PR build but via nightly
            # builds or similar so we also skip those
            if not pr_num or pr_num != current_pr_num:
                continue

            # Execution is considered as old if build_num is < current build num
            if build_num and build_num < current_build_num:
                result.apend(execution_api)

        return result

    def _get_client(self):
        base_url, api_url, auth_url = self._get_st2_urls()

        client_kwargs = {
            'base_url': base_url,
            'api_url': api_url,
            'auth_url': auth_url,
        }

        token = self._get_auth_token()
        client_kwargs['token'] = token

        return Client(**client_kwargs)

    def _get_st2_urls(self):
        base_url = None
        api_url = os.environ.get('ST2_ACTION_API_URL', None)
        auth_url = os.environ.get('ST2_ACTION_AUTH_URL', None)

        return base_url, api_url, auth_url

    def _get_auth_token(self):
        token = os.environ.get('ST2_ACTION_AUTH_TOKEN', None)
        return token
