export interface Child {
	_key: string;
	_type: string;
	marks: string[];
	text: string;
}

export interface Event {
	_key: string;
	_type: string;
	children: Child[];
	markDefs: any[];
	style: string;
}

export interface ImageUrl {
	_key: string;
	_type: string;
	height: string;
	urlField: string;
	url_title: string;
	width: string;
}

export interface Person {
	_key: string;
	_ref: string;
	_type: string;
}

export interface SourceUrl {
	_key: string;
	_type: string;
	urlField: string;
	url_title: string;
}

export interface Timeline {
	_createdAt: Date;
	_id: string;
	_rev: string;
	_type: string;
	_updatedAt: Date;
	date: string;
	event: Event[];
	image_urls: ImageUrl[];
	order: number;
	people: Person[];
	source: string;
	tags: string[];
	time: string;
	title: string;
	type: string;
	source_urls: SourceUrl[];
}

export interface PersonRef {
	_id: string;
	name: string;
}
