-- Create the enum type first
DO $$ BEGIN
    CREATE TYPE "status" AS ENUM ('development', 'staging', 'production');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create the workflows table
CREATE TABLE IF NOT EXISTS "workflows" (
    "id" uuid PRIMARY KEY NOT NULL,
    "title" varchar(200) NOT NULL,
    "description" text,
    "status" "status" NOT NULL,
    "trace_api_key" varchar(200),
    "trace_project" varchar(200),
    "env_json" json NOT NULL,
    "user_id" uuid
);

-- Add the foreign key constraint
DO $$ BEGIN
    ALTER TABLE "workflows" ADD CONSTRAINT "workflows_user_id_User_id_fk" 
    FOREIGN KEY ("user_id") REFERENCES "public"."User"("id") 
    ON DELETE SET NULL 
    ON UPDATE NO ACTION;
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;