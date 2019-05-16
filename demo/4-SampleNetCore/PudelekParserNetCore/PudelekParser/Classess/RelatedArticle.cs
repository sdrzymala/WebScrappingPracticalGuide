using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel;

namespace WebScrapingPudelekPL.Classes
{
    public class RelatedArticle
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int related_article_id { get; set; }

        public int? article_id { get; set; }

        [StringLength(2500)]
        public string related_article_text { get; set; }

        [StringLength(2500)]
        public string related_article_url { get; set; }
    }
}
