// lib/azureRepoConnector.js

class AzureRepoConnector {

  constructor() {
    this.organization =  "RecallSpace";
    this.project =  "recall-space-developments";
    this.repository ="workflows";
    this.patToken = process.env.AZURE_PAT_TOKEN;

    if (!this.organization || !this.project || !this.repository || !this.patToken) {
      throw new Error('Azure configuration is missing. Please set the environment variables.');
    }

    this.baseUrl = `https://dev.azure.com/${this.organization}/${this.project}/_apis/git/repositories/${this.repository}`;
    this.apiVersion = '7.0';

    // Prepare the Authorization header
    const authStr = Buffer.from(`:${this.patToken}`).toString('base64');
    this.authHeader = `Basic ${authStr}`;
  }

  // Method to get a file's content
  async getFile(filePath, branch = 'dev') {
    const url = `${this.baseUrl}/items`;
    const params = new URLSearchParams({
      path: filePath,
      'versionDescriptor.version': branch,
      'versionDescriptor.versionType': 'branch',
      'api-version': this.apiVersion,
      download: 'true',
    });

    const response = await fetch(`${url}?${params.toString()}`, {
      headers: {
        Authorization: this.authHeader,
      },
    });

    if (response.status === 200) {
      const content = await response.text();
      return content;
    } else if (response.status === 404) {
      console.log(`File not found: ${filePath}`);
      return null;
    } else {
      const errorText = await response.text();
      throw new Error(`Error: ${response.status} ${errorText}`);
    }
  }

  // Method to update or create a file
  async updateFile(filePath, content, branch = 'dev', commitMessage = 'Updating file') {
    let latestCommit = await this._getLatestCommit(branch);
    console.log(`Latest commit ID on branch '${branch}': ${latestCommit}`);

    const contentBase64 = Buffer.from(content, 'utf-8').toString('base64');

    let fileExists;

    if (latestCommit) {
      // Branch exists
      console.log(`Branch '${branch}' exists. Latest commit ID: ${latestCommit}`);
      fileExists = await this._checkFileExists(filePath, branch);
      console.log(`File exists at '${filePath}': ${fileExists}`);
    } else {
      // Branch does not exist; set oldObjectId to zeros to create a new branch
      latestCommit = '0000000000000000000000000000000000000000';
      fileExists = false;
      console.log(`Branch '${branch}' does not exist. It will be created with the initial commit.`);
    }

    const changeType = fileExists ? 'edit' : 'add';

    const data = {
      refUpdates: [
        { name: `refs/heads/${branch}`, oldObjectId: latestCommit },
      ],
      commits: [
        {
          comment: commitMessage,
          changes: [
            {
              changeType: changeType,
              item: { path: filePath },
              newContent: {
                content: contentBase64,
                contentType: 'base64encoded',
              },
            },
          ],
        },
      ],
    };

    const url = `${this.baseUrl}/pushes?api-version=${this.apiVersion}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: this.authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (response.status === 201) {
      const action = fileExists ? 'Updated' : 'Created';
      console.log(`File ${action}: ${filePath}`);
    } else {
      const errorText = await response.text();
      console.error(`Error updating file: ${response.status} - ${errorText}`);
      throw new Error(`Error updating file: ${response.status} - ${errorText}`);
    }
  }

  // Method to delete a file
  async deleteFile(filePath, branch = 'main', commitMessage = 'Deleting file') {
    const latestCommit = await this._getLatestCommit(branch);

    const data = {
      refUpdates: [
        { name: `refs/heads/${branch}`, oldObjectId: latestCommit },
      ],
      commits: [
        {
          comment: commitMessage,
          changes: [
            { changeType: 'delete', item: { path: filePath } },
          ],
        },
      ],
    };

    const url = `${this.baseUrl}/pushes?api-version=${this.apiVersion}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: this.authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (response.status === 201) {
      console.log(`File deleted: ${filePath}`);
    } else {
      const errorText = await response.text();
      throw new Error(`Error deleting file: ${response.status} ${errorText}`);
    }
  }

  // Method to revert a file to a specific commit
  async revertFile(filePath, commitId, branch = 'main', commitMessage = 'Reverting file') {
    const content = await this._getFileAtCommit(filePath, commitId);
    if (content == null) {
      console.log(`File not found at commit ${commitId}: ${filePath}`);
      return;
    }

    // Update the file with the old content
    await this.updateFile(filePath, content, branch, commitMessage);
  }

  // Helper method to get the latest commit ID
  async _getLatestCommit(branch) {
    const url = `${this.baseUrl}/refs`;
    const params = new URLSearchParams({
      filter: `heads/${branch}`,
      'api-version': this.apiVersion,
    });

    const response = await fetch(`${url}?${params.toString()}`, {
      headers: {
        Authorization: this.authHeader,
      },
    });

    if (response.status === 200) {
      const data = await response.json();
      const refs = data.value;
      if (refs && refs.length > 0) {
        const latestCommit = refs[0].objectId;
        return latestCommit;
      } else {
        // Branch does not exist
        return null;
      }
    } else {
      const errorText = await response.text();
      throw new Error(`Error getting latest commit: ${response.status} ${errorText}`);
    }
  }

  // Helper method to check if a file exists
  async _checkFileExists(filePath, branch) {
    const url = `${this.baseUrl}/items`;
    const params = new URLSearchParams({
      path: filePath,
      'versionDescriptor.version': branch,
      'versionDescriptor.versionType': 'branch',
      'api-version': this.apiVersion,
    });

    const response = await fetch(`${url}?${params.toString()}`, {
      headers: {
        Authorization: this.authHeader,
      },
    });

    if (response.status === 200) {
      return true;
    } else if (response.status === 404) {
      return false;
    } else {
      const errorText = await response.text();
      throw new Error(`Error checking if file exists: ${response.status} ${errorText}`);
    }
  }

  // Helper method to get a file's content at a specific commit
  async _getFileAtCommit(filePath, commitId) {
    const url = `${this.baseUrl}/items`;
    const params = new URLSearchParams({
      path: filePath,
      'versionDescriptor.version': commitId,
      'versionDescriptor.versionType': 'commit',
      includeContent: 'true',
      'api-version': this.apiVersion,
    });

    const response = await fetch(`${url}?${params.toString()}`, {
      headers: {
        Authorization: this.authHeader,
      },
    });

    if (response.status === 200) {
      const data = await response.json();
      const contentBase64 = data.content;
      if (contentBase64) {
        const content = Buffer.from(contentBase64, 'base64').toString('utf-8');
        return content;
      } else {
        return null;
      }
    } else {
      return null;
    }
  }
}

module.exports = AzureRepoConnector;