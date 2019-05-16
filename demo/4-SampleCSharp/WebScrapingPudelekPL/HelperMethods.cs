using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace WebScrapingPudelekPL
{
    public class HelperMethods
    {
        public static string CleanText(string str)
        {
            return RemoveMultipleSpaces(RemoveSpecialCharacters(str)).Trim().ToLower();
        }

        public static string RemoveSpecialCharacters(string str)
        {
            StringBuilder sb = new StringBuilder();

            for (int i = 0; i < str.Length; i++)
            {
                if (char.IsLetterOrDigit(str[i]) || str[i] == ' ')
                {
                    sb.Append(str[i]);
                }
                else
                {
                    sb.Append(' ');
                }
            }

            return sb.ToString();
        }

        public static string RemoveMultipleSpaces(string str)
        {
            return Regex.Replace(str, @"\s+", " ");
        }

        //public static string RemoveSpecialCharacters(string str)
        //{
        //    StringBuilder sb = new StringBuilder();
        //    foreach (char c in str)
        //    {
        //        if ((c >= '0' && c <= '9') || (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || c == ' ')
        //        {
        //            sb.Append(c);
        //        }
        //    }
        //    return sb.ToString();
        //}

        //public static string RemoveSpecialCharacters(string str)
        //{
        //    return Regex.Replace(str, "[^a-zA-Z0-9 ]+", "", RegexOptions.Compiled);
        //}
    }
}
