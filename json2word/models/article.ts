import { Body, Slug, BaseDocument, ArticleUrl } from "./base";

export interface Article extends BaseDocument {
	articleUrls?: ArticleUrl[];
	author?: string;
	body?: Body[];
	category?: string;
	description?: string;
	featured?: boolean;
	mainImageUrl?: string;
	publishedAt: string;
	writtenAt: string;
	slug: Slug;
	tags?: string[];
	title: string;
}
