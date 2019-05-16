namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class update15 : DbMigration
    {
        public override void Up()
        {
            AddColumn("dbo.Tags", "TagText", c => c.String(maxLength: 255));
            AddColumn("dbo.Tags", "TagUrl", c => c.String(maxLength: 255));
            DropColumn("dbo.Tags", "TagName");
        }
        
        public override void Down()
        {
            AddColumn("dbo.Tags", "TagName", c => c.String(maxLength: 255));
            DropColumn("dbo.Tags", "TagUrl");
            DropColumn("dbo.Tags", "TagText");
        }
    }
}
