export interface Child {
	_key: string;
	_type: string;
	marks: any[];
	text: string;
}

export interface Content {
	_key: string;
	_type: string;
	children: Child[];
	markDefs: any[];
	style: string;
}

export interface Slug {
	_type: string;
	current: string;
}

export interface About {
	_createdAt: Date;
	_id: string;
	_rev: string;
	_type: string;
	_updatedAt: Date;
	content: Content[];
	quote?: string;
	slug: Slug;
	title: string;
	subtitle: string;
	footer?: string[];
}
