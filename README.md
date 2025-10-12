# Astro Netlify Sanity Starter

![Astro Netlify Sanity Starter](https://assets.stackbit.com/docs/astro-sanity-starter-thumb.jpg)

[Live Demo](https://astro-sanity-starter-demo.netlify.app/)

Netlify Astro and Sanity minimal starter with [visual editing](https://docs.netlify.com/visual-editor/overview/).

| Prerequisites                                                                |
| :--------------------------------------------------------------------------- |
| [Node.js](https://nodejs.org/) v20.+                                         |
| (optional) [nvm](https://github.com/nvm-sh/nvm) for Node version management. |

## Getting Started

Create local project from this repo and run:

```txt
npm install
```

### Sign Into Sanity

If you are not already signed into Sanity via the CLI, install the CLI package and then run the login command.

```txt
npm install -g @sanity/cli
sanity login
```

This will open a browser and walk you through the authentication process.

### Import Content

Once authenticated, you'll be able to create a Sanity project and import content.

```txt
npm run create-project
```

_Note: You may want to sign into Sanity in the browser and rename your project._

Once the project exists and you've set the environment variables, you can import the content.

```txt
npm run import {projectId}
```

Replace `{projectId}` with the project ID output from the previous command.

### Store Sanity Values

Sign into Sanity to create an editor token, navigate to the following address (replace the `SANITY_PROJECT_ID` with your project ID) `https://www.sanity.io/manage/personal/project/SANITY_PROJECT_ID/api#tokens`. Then create `.env` file in you repo, copy & paste the following environment variables into the file and set their values.

```txt
SANITY_PROJECT_ID="..."
SANITY_DATASET="..."
SANITY_TOKEN="..."
```

### Run Sanity Studio

Sanity Studio code exists for this project in the `studio` directory. First, install the dependencies in this directory.

```txt
cd studio
npm install
```

Then create a `.env` file in the `studio` directory with the following environment variables and set their values:

```txt
SANITY_STUDIO_PROJECT_ID="..."
SANITY_STUDIO_DATASET="..."
```

Then run the studio locally.

```txt
sanity dev
```

If you want to see the content, you can open your browser and navigate to localhost:3333.

### Start Development Server

Then you can run the Astro.js development server in root directory:

```txt
npm run dev
```

Install Netlify Visual Editor CLI:

```txt
npm install -g @stackbit/cli
```

And the Stackbit development server.

```txt
stackbit dev
```

This outputs your own Netlify Visual Editor URL. Open this, register or sign in, and you will be directed to Netlify Visual Editor for your new project.

## Next Steps

Here are a few suggestions on what to do next if you're new to Netlify Visual Editor:

- Learn [how Netlify Visual Editor works](https://docs.netlify.com/visual-editor/concepts/how-visual-editor-works/)
- Check [Netlify Visual Editor reference documentation](https://visual-editor-reference.netlify.com/)

## Support

If you get stuck along the way, get help in our [support forums](https://answers.netlify.com/).

## Django AI Assistant API

This repository also contains a standalone Django project in `django_ai_app/` that exposes a REST API and AI-powered chat
assistant capable of performing CRUD operations on knowledge base documents and reading files from the project.

### Prerequisites

- [Python](https://www.python.org/) 3.11+
- An [OpenAI API key](https://platform.openai.com/)

### Setup

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   cd django_ai_app
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables. The Django project reads standard Django settings plus the following:

   ```bash
   export OPENAI_API_KEY="sk-..."
   export OPENAI_MODEL="gpt-4.1-mini"  # Optional, defaults to gpt-4.1-mini
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`.

### API Overview

- `POST /api/chat/`: Sends a message to the AI assistant. The assistant will decide whether to respond directly, manage
  documents, or read project files. Example payload:

  ```json
  {
    "message": "Create a document titled Release Plan with bullet points from README",
    "history": [
      {"role": "user", "content": "List all documents"},
      {"role": "assistant", "content": "Currently there are no documents."}
    ]
  }
  ```

- CRUD endpoints for documents are provided by the REST router:
  - `GET /api/documents/`
  - `POST /api/documents/`
  - `GET /api/documents/{id}/`
  - `PATCH /api/documents/{id}/`
  - `DELETE /api/documents/{id}/`

### Running Tests

Inside `django_ai_app/` run:

```bash
python manage.py test
```

The included tests cover document CRUD endpoints and validation helpers used by the chat view.
