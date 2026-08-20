# settings

Where customer configuration data is stored. 

See the [Github Simplified Notion page](https://www.notion.so/Github-Simplified-1386145079d180d8917ad32046ea7d1f) for best practices, including forking.

## LFS (Large File Storage)

Large files are stored in [git LFS](https://git-lfs.com/) which means the large file is replaced with a hash in git history, keeping the repository smaller. This should not have any impact on day-to-day activities.

First time users should install LFS with:

```bash
git lfs install
```

Tracked file extensions will appear in [.gitattributes](.gitattributes). Use `git lfs track *.ply` to track any file with a `.ply` extension.

List which files are tracked with LFS in a repo with `git lfs ls-files`. See `man git lfs` for details.

