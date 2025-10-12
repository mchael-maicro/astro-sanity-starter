import { client, hasSanityCredentials } from '@utils/sanity-client';
import { IMAGE } from './blocks';

const CONFIG_QUERY_OBJ = `{
  _id,
  "favicon": {
    "src": favicon.asset->url
  },
  header {
    ...,
    logo ${IMAGE}
  },
  footer,
  titleSuffix
}`;

const FALLBACK_CONFIG = {
    _id: 'local-site-config',
    titleSuffix: 'Hearthside Atlas Realty',
    header: {
        title: 'Hearthside Atlas Realty',
        navLinks: [
            { _type: 'actionLink', label: 'Properties', url: '#properties' },
            { _type: 'actionLink', label: 'Buying Philosophy', url: '#philosophy' },
            { _type: 'actionLink', label: 'Market Pulse', url: '#market' },
            { _type: 'actionLink', label: 'Work With Me', url: '#contact' }
        ]
    },
    footer: {
        text: `**Hearthside Atlas Realty**  ·  Curated by your opinionated neighborhood scout.\\n` +
            `Let's talk strategy: [hello@hearthsideatlas.com](mailto:hello@hearthsideatlas.com) · (555) 011-4578`
    }
};

export async function fetchData() {
    if (!hasSanityCredentials) {
        return FALLBACK_CONFIG;
    }

    try {
        const data = await client.fetch(`*[_type == "siteConfig"][0] ${CONFIG_QUERY_OBJ}`);
        return data ?? FALLBACK_CONFIG;
    } catch (error) {
        console.warn('Using fallback site config because Sanity fetch failed.', error);
        return FALLBACK_CONFIG;
    }
}
