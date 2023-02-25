// import S3 from "aws-sdk/clients/s3";
import { S3 } from "@aws-sdk/client-s3";
import { keyid, secret, accountid } from "../../credential";

const fs = require("fs");

const s3 = new S3({
	endpoint: `https://${accountid}.r2.cloudflarestorage.com`,
	credentials: {
		accessKeyId: `${keyid}`,
		secretAccessKey: `${secret}`,
	},
	region: "us-east-1",
	apiVersion: "v4",
});

export const downloadImageS3 = async function (
	basedir: string,
	obj_name: string,
	target_name: string
) {
	const savePath = `${basedir}/${target_name}`;

	try {
		if (fs.existsSync(savePath)) {
			console.log(`existed ${savePath}, skip`);
			return;
		}
	} catch (err: any) {
		console.log(err);
	}
	const obj = await s3.getObject({
		Bucket: "lxexpress",
		Key: obj_name.replaceAll("\\", "/"),
	});
	console.log(`Downloading ${savePath}`);
	const buffer = await obj.Body?.transformToByteArray();
	fs.writeFileSync(savePath, buffer);
};

// let key =
// 	"3观者评说\\Qhja365\\案情推理\\20171213_日本庭审刘鑫和法医回答提问情况对比\\20171213_日本庭审刘鑫和法医回答提问情况对比_01_刘鑫文章《致江女士：言尽于此》_检方要求记不清就说记不清.jpg";

// const run = async () => {
// 	// const obj = await s3.getObject({
// 	// 	Bucket: "lxexpress",
// 	// 	Key: key,
// 	// });
// 	const obj = await s3.listObjects({
// 		Bucket: "lxexpress",
// 		Prefix: "3观者评说",
// 	});
// 	let key1 = key.replaceAll("\\", "/");
// 	console.log(key1);
// 	fs.writeFileSync("tmp.json", JSON.stringify(obj.Contents));
// 	console.log(obj.Contents?.filter((content) => content.Key == key1));
// };

// run();
