This is a work-in-progress port of <https://github.com/Gewerd-Strauss/ObsidianKnittr>.

Note:

- this port aims to mostly refactor and streamline the codebase for the sake of
  - further development
  - easier modification by user
  - generally being less janky than the original AHK-instance

- it will not be a 1:1 feature-identical port, certain things might be altered/dropped for any reason. As this is not an ongoing transition away from the ahk-instance, no deprecation-warnings will be issued.
  - I attempt to keep the number of dropped features to a minimum
  - at the same time, reaching a high degree of feature parity can and will take time.
- unless the version (set in `obsidianknittrpy\__init__.py` via `__version__`) is flagged as a development version (`X.Y.Z.9000`), consider this project still in active development and potentially rapidly changing in any of its interfaces.
- development might take some time, as I do have substantially more important things going on, with this being a side-project for me.
- still, feedback/suggestions are welcome.

- and finally, the emerging documentation will be handled in the `docs`-branch (#TODO: create update-bash for the branch, set up obsidian-vault within, ignore all else; set up obsidianhtml-pipeline and build website from the html-output. Not sure how yet, but somehow for sure. Vault should be not require the install of this package to generate the vault online. Maybe create an org to have the CI/CL necessary? Consider <https://obsidian-html.github.io/automation/automate-website-deployment.html>)
