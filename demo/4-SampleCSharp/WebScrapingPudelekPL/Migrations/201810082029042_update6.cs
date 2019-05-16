namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class update6 : DbMigration
    {
        public override void Up()
        {
            AddColumn("dbo.Articles", "InsertedAt", c => c.DateTime());
        }
        
        public override void Down()
        {
            DropColumn("dbo.Articles", "InsertedAt");
        }
    }
}
