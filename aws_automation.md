don't ask for full AWS account permissions.

Ask users to create a dedicated IAM user.

IAM policy should ONLY allow:
{
 "Version":"2012-10-17",

 "Statement":[
   {
    "Effect":"Allow",

    "Action":[
      "s3:GetObject",
      "s3:ListBucket"
    ],

    "Resource":[
      "arn:aws:s3:::carboniq-cur-bucket",
      "arn:aws:s3:::carboniq-cur-bucket/*"
    ]
   }
 ]
}
This is VERY IMPORTANT.

Never ask for:

AdministratorAccess

❌

Examiner will roast you.

What should users enter?

One-time setup:

Access Key

Secret Key

Bucket Name

AWS Region

CUR Folder Path

Example:

Bucket:
carboniq-cur-bucket

Region:
ap-south-1

Path:
carboniq-reports/
Then CarbonIQ stores:
NOT the password.

Store:

User

↓

AWS Connection Profile

Example:

User ID

AWS Account ID

Bucket Name

Bucket Region

CUR Prefix

Encrypted Secret ID