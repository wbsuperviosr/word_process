import { downloadImageS3 } from "./awss3";
import { downloadImageHTTP } from "./http";

export async function downloadImage(
	basedir: string,
	target_name: string,
	link: string
) {
	if (link.startsWith("http")) {
		await downloadImageHTTP(basedir, link, target_name);
	} else {
		await downloadImageS3(basedir, link, target_name);
	}
}

// import { CaseFile } from "../models/casefilesModel";
// const casefiles: CaseFile[] = require("../data/casefiles.json");
// for (const casefile of casefiles) {
// 	if (casefile.image_urls) {
// 		for (const [index, image_url] of casefile.image_urls.entries()) {
// 			downloadImage(
// 				"./images/casefile/",
// 				image_url.urlField,
// 				`${casefile.title}_${index}.jpg`
// 			);
// 		}
// 	}
// }
