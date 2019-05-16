using PostSharp.Aspects;
using System;
using System.Collections.Generic;
using System.Text;
using PostSharp.Patterns.Diagnostics;
using PostSharp.Extensibility;


[assembly: Log(AttributePriority = 1, AttributeTargetMemberAttributes = MulticastAttributes.Protected | MulticastAttributes.Internal | MulticastAttributes.Public)]
[assembly: Log(AttributePriority = 2, AttributeExclude = true, AttributeTargetMembers = "get_*" )]

namespace PudelekParser
{

    [Serializable]
    public class timeit : MethodInterceptionAspect
    {
        public override void OnInvoke(MethodInterceptionArgs args)
        {
            Console.WriteLine("OnInvoke! before");
            Console.WriteLine("OnInvoke! after");
        }
    }
}
