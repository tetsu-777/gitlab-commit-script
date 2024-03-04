import subprocess
import json

DEBUG = True
GITLAB_API_ENDOPOINT = 'https://gitlab.example.com/api/v4'

class gitlab:
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
                self(gitlab class) : 第一引数
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
