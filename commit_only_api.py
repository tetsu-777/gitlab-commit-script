import subprocess
import json

DEBUG = True
GITLAB_API_ENDOPOINT = 'https://gitlab.example.com/api/v4'


class gitlab:

    """API通信時に必要な情報をまとめたい（Issue/Branches/Commits/Merge Requests API通信時のリクエストで共通の使用するデータを毎回APIを呼び出したくない、、）
        api_information = {
            "mr_title": string(MRのタイトル),
            "issue_id": int(作成したIssueのID),
            "source_branch": string(開発ブランチ名),
            "assignee_id": int(ユーザーID),
            "mr_description": string(MR概要)
        }
    """
    api_information = {}

    def __init__(self, url, personal_access_token, source_project_name, source_commit_sha, target_project_name, target_branch_name):
        self.url = url
        self.personal_access_token = personal_access_token
        self.source_project_name = source_project_name
        self.source_commit_sha = source_commit_sha
        self.target_project_name = target_project_name
        self.target_branch_name = target_branch_name


    def get_file_changes_from_commit_sha(self):
        """ コミットsha番号からファイルの変更情報を取得する
            Args:
                None
            Returns
                list: file_changes(ファイルの変更情報)
                期待されるデータ例
                    [
                        {
                            "diff": "@@ -71,6 +71,8 @@\n sudo -u git -H bundle exec rake migrate_keys RAILS_ENV=production\n sudo -u git -H bundle exec rake migrate_inline_notes RAILS_ENV=production\n \n+sudo -u git -H bundle exec rake gitlab:assets:compile RAILS_ENV=production\n+\n ```\n \n ### 6. Update config files",
                            "new_path": "doc/update/5.4-to-6.0.md",
                            "old_path": "doc/update/5.4-to-6.0.md",
                            "a_mode": null,
                            "b_mode": "100644",
                            "new_file": false,
                            "renamed_file": false,
                            "deleted_file": false
                        }, ...
                    ]
        """
        api_url = f'{GITLAB_API_ENDOPOINT}/projects/{self.source_project_name}/repository/commits/{self.source_commit_sha}/diff'
        header = f'PRIVATE-TOKEN: {self.personal_access_token}'
        try:
            result = subprocess.run(['curl', '--header', header, '--url', api_url], capture_output=True, text=True, check=True)
        except Exception as e:
            if DEBUG:
                print(f'subprocess command error: {e}')
            raise Exception('subprocessコマンドの実行に失敗しました。\nコミットsha番号:{self.source_commit_sha}')
        output = result.stdout
        if DEBUG:
            print(f'Commits API response:\n{output}')
        if '404' in output:
            raise Exception(f'指定のコミットを取得できませんでした。\nコミットsha番号:{self.source_commit_sha}')
        # json.loads() 関数を使用して文字列をPythonのリスト型に変換
        file_changes = json.loads(output)
        return file_changes


    def commit_cherrypick_information_for_mr(self):
        """ コミット単位でのcherrypick実行時の際、MR作成に必要な情報（title, description）を取得・成形する
            Args:
                None
            Returns
                None
        """
        # titleデータの取得・成形
        api_url = f'{GITLAB_API_ENDOPOINT}/projects/{self.source_project_name}/repository/commits/{self.source_commit_sha}'
        header = f'PRIVATE-TOKEN: {self.personal_access_token}'
        try:
            result = subprocess.run(['curl', '--header', header, '--url', api_url], capture_output=True, text=True, check=True)
        except Exception as e:
            if DEBUG:
                print(f'subprocess command error: {e}')
            raise Exception('subprocessコマンドの実行に失敗しました。\nコミットsha番号:{self.source_commit_sha}')
        output = result.stdout
        if DEBUG:
            print(f'Commits API response:\n{output}')
        if '404' in output:
            raise Exception(f'指定のコミットを取得できませんでした。\nコミットsha番号:{self.source_commit_sha}')
        # json.loads() 関数を使用して文字列をPythonの辞書型に変換
        commit_infomation = json.loads(output)

        self.api_information['mr_title'] = commit_infomation['title']

        description = f'{commit_infomation['title']}\n{commit_infomation['short_id']}'
        self.api_information['description'] = description

