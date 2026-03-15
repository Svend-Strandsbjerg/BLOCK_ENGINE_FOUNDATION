# Publishing to npm

This repository is configured to publish as `@block-engine/foundation`.

## Manual publish

1. Ensure your npm account can publish the package (`npm whoami`).
2. Build and validate the package locally:

   ```bash
   npm install
   npm run prepublishOnly
   ```

3. Publish to npm:

   ```bash
   npm publish --access public
   ```

## Publish via GitHub Actions

1. Add an npm automation token to repository secrets as `NPM_TOKEN`.
2. Trigger `.github/workflows/npm-publish.yml` manually from **Actions** OR push a version tag like `v0.1.0`.
3. The workflow will install dependencies, build `dist/`, and publish using `NODE_AUTH_TOKEN=${{ secrets.NPM_TOKEN }}`.

## Versioning notes

- Update `package.json` version before release.
- For tag-based publishing, create and push a matching `v<version>` tag.
