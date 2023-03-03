import { Body, Slug, BaseDocument } from "./base";

export interface Media extends BaseDocument {
	title: string;
	subtitle?: string;
	slug: Slug;
	author?: string;
	mediaUrl?: string;
	category?: string;
	tags?: string[];
	mainImageUrl?: string;
	description?: string;
	body?: Body[];
	publishedAt?: string;
	writtenAt?: string;
	downloadLink?: string;
	downloadMeta?: string;
}
