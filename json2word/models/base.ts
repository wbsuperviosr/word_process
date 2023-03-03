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
	urlField: string;
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
