import fetch from "cross-fetch";
import { S3 } from "@aws-sdk/client-s3";

type SanityConfig = {
	token?: string;
	dev_token?: string;
	project_id?: string;
	dev_project_id?: string;
	dataset?: string;
	api_version?: string;
};

class SanityService {
	config: SanityConfig;
	dev: boolean;
	constructor(config: SanityConfig, dev: boolean) {
		this.config = config;
		this.dev = dev;
	}

	async get(query: string) {
		const response = await fetch(`${this.query_api}?query=${query}`, {
			headers: this.headers,
		});
		return await response.json();
	}

	async get_documents(type: string) {
		const query = `*[_type=='${type}']`;
		const response = await this.get(query);
		return response["result"];
	}

	async get_document(type: string, title: string) {
		const query = `*[_type=='${type}' %26%26 title=='${title}']`;
		const response = await this.get(query);
		return response.result[0];
	}

	get query_api() {
		return `${this.endpoint}/data/query/${this.config.dataset}`;
	}

	get endpoint() {
		return `https://${this.project_id}.api.sanity.io/${this.config.api_version}`;
	}

	get headers() {
		return { authorization: `Bearer ${this.token}` };
	}

	get token() {
		if (this.dev) {
			return this.config.dev_token;
		}
		return this.config.token;
	}

	get project_id() {
		if (this.dev) {
			return this.config.dev_project_id;
		}
		return this.config.project_id;
	}
}

class CloudflareService {
	constructor(public config: CloudflareConfig) {
		this.config = config;
	}

	async getFile(filename: string) {
		const obj = this.s3.getObject({
			Bucket: this.config.bucket,
			Key: filename.replaceAll("\\", "/"),
		});
		return await (await obj).Body?.transformToByteArray();
	}

	get s3(): S3 {
		return new S3({
			endpoint: `https://${this.config.account_id}.r2.cloudflarestorage.com`,
			credentials: {
				accessKeyId: `${this.config.key_id}`,
				secretAccessKey: `${this.config.secret}`,
			},
			region: "us-east-1",
			apiVersion: "v4",
		});
	}
}

class HttpImageService {
	async getFile(url: string) {
		const response = await fetch(url);
		const arrayBuffer = await response.arrayBuffer();
		const buffer = Buffer.from(arrayBuffer);
		return buffer;
	}
}

type CloudflareConfig = {
	account_id?: string;
	key_id?: string;
	secret?: string;
	bucket: string;
};

type ServiceConfig = {
	sanity?: SanityConfig;
	cloudflare?: CloudflareConfig;
};

export class Service {
	config: ServiceConfig;
	constructor(config: ServiceConfig) {
		this.config = config;
	}

	static from_file(crendital: string) {
		const config = require(crendital);
		return new Service(config);
	}
	get_sanity(dev: boolean) {
		return new SanityService(this.config.sanity!, dev);
	}

	get_cloudflare() {
		return new CloudflareService(this.config.cloudflare!);
	}

	get_httpimage() {
		return new HttpImageService();
	}
}

// const service = Service.from_file("../credential.json");

// let run = async () => {
// 	const client = service.get_sanity(true);
// 	let data = await client.get_documents("about");
// 	console.log(data);
// };

// run();
