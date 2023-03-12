interface BaseElement {
	_key: string;
	_type: string;
}

export interface ImageUrl extends BaseElement {
	height?: string;
	width?: string;
	urlField: string;
	urlTitle: string;
}

export interface ArticleUrl extends BaseElement {
	urlField: string;
	urlTitle: string;
}

export interface Child extends BaseElement {
	marks: string[];
	text: string;
}

export interface Reference extends BaseElement {
	title: string;
	urlField?: string;
}

export interface MarkDef extends BaseElement {
	reference: Reference[];
	href?: string;
}

export interface Slug {
	_type: string;
	current: string;
}

export interface Body extends BaseElement {
	children: Child[];
	markDefs: MarkDef[];
	style?: string;
	level?: number;
	listItem?: string;
}

export interface BaseDocument {
	_id: string;
	_rev: string;
	_type: string;
	_createdAt: string;
	_updatedAt: string;
}

export const FieldStringMap = new Map([
	["_id", "string"],
	["_rev", "string"],
	["_type", "string"],
	["_createdAt", "datetime"],
	["_updatedAt", "datetime"],
	["body", "body"],
	["category", "string"],
	["date", "string"],
	["time", "string"],
	["order", "number"],
	["tags", "listString"],
	["source", "string"],
	["people", "listString"],
	["imageUrls", "listImageUrl"],
	["articleUrls", "listArticleUrl"],
	["author", "string"],
	["description", "string"],
	["featured", "boolean"],
	["mainImageUrl", "string"],
	["publishedAt", "datetime"],
	["writtenAt", "datetime"],
	["slug", "slug"],
	["title", "string"],
	["header", "string"],
	["subtitle", "string"],
	["mediaUrl", "string"],
	["downloadLink", "string"],
	["downloadMeta", "string"],
	["importance", "number"],
	["rumorSpreader", "listString"],
	["rumorVictim", "listString"],
	["rumor", "body"],
	["rumorArticleUrls", "listArticleUrl"],
	["rumorImageUrls", "listImageUrl"],
	["truth", "body"],
	["truthArticleUrls", "listArticleUrl"],
	["truthImageUrls", "listImageUrl"],
	["footer", "listString"],
	["quote", "string"],
]);
