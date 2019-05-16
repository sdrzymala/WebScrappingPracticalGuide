namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class update51 : DbMigration
    {
        public override void Up()
        {
            AddColumn("dbo.Articles", "IsDownloaded", c => c.Boolean());
        }
        
        public override void Down()
        {
            DropColumn("dbo.Articles", "IsDownloaded");
        }
    }
}
