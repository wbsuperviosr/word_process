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
