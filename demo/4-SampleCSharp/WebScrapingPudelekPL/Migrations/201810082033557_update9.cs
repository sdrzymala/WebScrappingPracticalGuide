namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class update9 : DbMigration
    {
        public override void Up()
        {
            AlterColumn("dbo.Articles", "InsertedAt", c => c.DateTime());
        }
        
        public override void Down()
        {
            AlterColumn("dbo.Articles", "InsertedAt", c => c.DateTime());
        }
    }
}
