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
    public class Tag
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int tag_id { get; set; }

        public int? article_id { get; set; }

        [StringLength(255)]
        public string tag_text { get; set; }

        [StringLength(255)]
        public string tag_url { get; set; }
    }
}
