import { Body, BaseDocument, ArticleUrl, ImageUrl } from "./base";

export interface Timeline extends BaseDocument {
	body?: Body;
	category?: string;
	date?: string;
	time?: string;
	order?: number;
	tags?: string[];
	source?: string;
	people?: string[];
	articleUrls?: ArticleUrl[];
	imageUrls?: ImageUrl[];
}
