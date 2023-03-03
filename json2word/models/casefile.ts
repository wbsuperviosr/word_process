import { Body, Slug, BaseDocument, ImageUrl, ArticleUrl } from "./base";

export interface Casefile extends BaseDocument {
	body?: Body[];
	category?: string;
	description?: string;
	featured?: boolean;
	header?: string;
	mainImageUrl?: string;
	order?: number;
	slug: Slug;
	tags?: string[];
	title: string;
	writtenAt: string;
	publishedAt: string;
	imageUrls?: ImageUrl[];
	articleUrls?: ArticleUrl[];
}
