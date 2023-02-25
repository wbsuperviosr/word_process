export interface Author {
	_id: string;
	_ref: string;
	_type: string;
	name: string;
}

export interface Child {
	_key: string;
	_type: string;
	marks: string[];
	text: string;
	references?: number[];
}

export interface Reference {
	_key: string;
	_type: string;
	title: string;
	urlField: string;
}
export interface MarkDef {
	_key: string;
	_type: string;
	reference: Reference[];
	href: string;
}

export interface Body {
	_key: string;
	_type: string;
	children: Child[];
	markDefs: MarkDef[];
	style: string;
	level?: number;
	listItem: string;
}

export interface Slug {
	_type: string;
	current: string;
}

export interface Related {
	title: string;
	urlField: string;
	category: string;
}

export interface Post {
	_createdAt: Date;
	_id: string;
	_rev: string;
	_type: string;
	_updatedAt: Date;
	author: Author;
	body: Body[];
	category: string;
	description: string;
	mainImageUrl: string;
	publishedAt: Date;
	slug: Slug;
	tags: string[];
	title: string;
	writtenAt: Date;
	theme: string;
	featured?: boolean;
	related?: Related[];
}
