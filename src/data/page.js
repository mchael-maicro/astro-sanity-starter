import { client, hasSanityCredentials } from '@utils/sanity-client';
import { SECTIONS } from './blocks';

const PAGE_QUERY_OBJ = `{
  _id,
  slug,
  title,
  metaTitle,
  metaDescription,
  "socialImage": {
    "src": socialImage.asset->url
  },
  sections[] ${SECTIONS}
}`;

export async function fetchData() {
    if (!hasSanityCredentials) {
        return [];
    }

    try {
        return await client.fetch(`*[_type == "page"] ${PAGE_QUERY_OBJ}`);
    } catch (error) {
        console.warn('Falling back to an empty page collection because Sanity fetch failed.', error);
        return [];
    }
}

export async function getPageById(id) {
    if (!hasSanityCredentials) {
        return [];
    }

    try {
        return await client.fetch(`*[_type == "page" && _id == "${id}"] ${PAGE_QUERY_OBJ}`);
    } catch (error) {
        console.warn(`Falling back to an empty result for page ${id} because Sanity fetch failed.`, error);
        return [];
    }
}
