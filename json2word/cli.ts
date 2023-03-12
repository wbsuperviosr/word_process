import { parseArgs, ParseArgsConfig } from "util";
import { AboutEngine } from "./render/about";
import { ArticleEngine } from "./render/article";
import { CasefileEngine } from "./render/casefile";
import { IDocxConfig } from "./render/core";
import { Service } from "./service";
import { logger } from "./logger";
import { RumorEngine } from "./render/rumor";
import { TimelineEngine } from "./render/timeline";

export interface CliCommand {
	type: string;
	name: string;
	word_dir: string;
	image_dir: string;
}

const ParseConfig: ParseArgsConfig = {
	options: {
		type: {
			type: "string",
			short: "t",
		},
		title: {
			type: "string",
			short: "n",
		},
		no_cache: {
			type: "boolean",
			short: "c",
		},
		output_dir: {
			type: "string",
			short: "o",
			default: "mswords",
		},
		image_dir: {
			type: "string",
			short: "i",
			default: "images",
		},
		from_local: {
			type: "boolean",
			short: "l",
		},
	},
};

const buildArgs = () => {
	let args = parseArgs(ParseConfig);
	let { type, title, no_cache, output_dir, image_dir, from_local } =
		args.values;
	if (!type) {
		throw new Error("you must provide the document type");
	}

	const config: IDocxConfig = {
		docType: type as string,
		outputDir: output_dir ? (output_dir as string) : "mswords",
		imageDir: image_dir ? (image_dir as string) : "images",
		cacheImage: no_cache ? false : true,
		fromLocal: from_local ? true : false,
	};
	return [type, title, config];
};

const buildEngine = (type: string, config: IDocxConfig, service: Service) => {
	switch (type) {
		case "casefile":
			return new CasefileEngine(config, service);
		case "post":
		case "voice":
			return new ArticleEngine(config, service);
		case "about":
			return new AboutEngine(config, service);
		case "rumor":
			return new RumorEngine(config, service);
		case "timeline":
			return new TimelineEngine(config, service);
		default:
			logger.error(`unknown input type! ${type}`);
			break;
	}
};

const main = async () => {
	const service = Service.from_file("../credential.json");
	const [type, title, config] = buildArgs();
	const engine = buildEngine(type as string, config as IDocxConfig, service);
	engine?.run(title as string | undefined);
};

main();
