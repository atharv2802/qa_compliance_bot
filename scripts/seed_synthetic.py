import json
import os
import random
from pathlib import Path
from typing import List, Dict

def ensure_data_dir():
    """Create data directories if they don't exist."""
    Path("data/synthetic").mkdir(parents=True, exist_ok=True)

def generate_adv_cases() -> List[Dict]:
    """Generate ADV-6.2 violation cases (guarantee/risk-free claims)."""
    templates = [
        # Direct guarantees
        ("We guarantee {percent}% returns annually on this investment.", "Customer asking about expected returns", "high"),
        ("I can guarantee you'll see profits of at least {percent}% this year.", "Customer concerned about performance", "high"),
        ("This fund guarantees consistent returns regardless of market conditions.", "Explaining investment strategy", "high"),
        ("You're guaranteed to make money with our managed portfolio.", "Portfolio recommendation", "high"),
        ("We guarantee your investment will outperform the market.", "Customer comparing options", "high"),
        
        # Risk-free claims
        ("This is a completely risk-free investment opportunity.", "Customer asking about risks", "high"),
        ("There's zero risk involved - your principal is 100% guaranteed.", "Addressing safety concerns", "high"),
        ("You won't lose a penny with this risk-free strategy.", "Customer worried about losses", "high"),
        ("This account is risk-free and guarantees steady growth.", "Account recommendation", "high"),
        ("It's totally safe and risk-free, with guaranteed returns.", "Reassuring nervous customer", "high"),
        
        # Promise/assurance violations
        ("I promise you'll see excellent returns within six months.", "Timeline discussion", "high"),
        ("I can assure you this investment will pay off handsomely.", "Encouraging hesitant customer", "high"),
        ("You'll definitely see your money grow by at least {percent}%.", "Setting expectations", "high"),
        ("This strategy ensures you'll always come out ahead.", "Strategy explanation", "high"),
        ("We promise consistent profits year after year.", "Long-term planning discussion", "high"),
        
        # Comparative guarantees
        ("We guarantee better returns than any competitor in the market.", "Competitive comparison", "high"),
        ("Our guaranteed yields are the highest you'll find anywhere.", "Marketing pitch", "high"),
        ("No other firm can guarantee the returns we deliver.", "Differentiating from competitors", "high"),
        
        # Specific scenarios
        ("Based on our track record, I can guarantee you'll see {percent}% gains.", "Reviewing historical data", "high"),
        ("This retirement account guarantees you'll have enough to retire comfortably.", "Retirement planning", "high"),
        ("Your college fund is guaranteed to cover all tuition costs.", "Education planning", "high"),
        ("We guarantee this investment will beat inflation every year.", "Inflation concerns", "high"),
        ("I guarantee you won't regret choosing this portfolio.", "Closing sale", "high"),
        
        # Conversational violations
        ("Look, I can personally guarantee this will work out for you.", "Building trust with customer", "high"),
        ("Trust me, this is a guaranteed winner - I've seen it work for hundreds of clients.", "Sharing experience", "high"),
        ("Between you and me, this is basically guaranteed money.", "Creating urgency", "high"),
        ("I'd put my own money in this guaranteed investment in a heartbeat.", "Personal endorsement", "high"),
        ("Every single client who's invested here has seen guaranteed positive returns.", "Success story sharing", "high"),
        
        # Time-based guarantees
        ("You're guaranteed to see returns within the first quarter.", "Short-term expectations", "high"),
        ("I guarantee you'll double your money in three years.", "Long-term projection", "high"),
        ("This investment guarantees monthly income starting immediately.", "Income generation", "high"),
        
        # Complex scenarios
        ("While past performance doesn't indicate future results, I can guarantee similar outcomes.", "Performance discussion with disclaimer", "high"),
        ("Even though markets fluctuate, we guarantee consistent returns for our clients.", "Market volatility discussion", "high"),
        ("This diversified portfolio guarantees protection against market downturns.", "Risk mitigation discussion", "high"),
    ]
    
    cases = []
    percents = [5, 8, 10, 12, 15, 18, 20, 25]
    
    for template, context, severity in templates:
        if "{percent}" in template:
            for pct in random.sample(percents, 3):
                cases.append({
                    "policy_id": "ADV-6.2",
                    "agent_draft": template.format(percent=pct),
                    "context": context,
                    "severity": severity
                })
        else:
            cases.append({
                "policy_id": "ADV-6.2",
                "agent_draft": template,
                "context": context,
                "severity": severity
            })
    
    return cases

def generate_pii_cases() -> List[Dict]:
    """Generate PII-SSN violation cases."""
    ssn_formats = [
        "123-45-6789", "987-65-4321", "555-44-3333", "111-22-3333",
        "777-88-9999", "222-33-4444", "666-55-7777", "444-33-2222",
        "888-77-6666", "333-22-1111", "999-88-7777", "123456789",
        "987654321", "555443333", "111223333"
    ]
    
    templates = [
        ("Your social security number {ssn} is on file for verification.", "Account verification", "critical"),
        ("I've located your account using SSN {ssn}.", "File lookup", "critical"),
        ("For security purposes, I need to confirm your SSN {ssn}.", "Identity confirmation", "critical"),
        ("The SSN you provided ({ssn}) matches our records.", "Verification check", "critical"),
        ("I see your full social {ssn} here in the system.", "System lookup", "critical"),
        ("Let me pull up your account - I have SSN {ssn} showing.", "Account access", "critical"),
        ("Your account ending in {last4} has full SSN {ssn} registered.", "Account details", "critical"),
        ("I've updated your records with SSN {ssn}.", "Record update", "critical"),
        ("The social security number {ssn} is required for this transaction.", "Transaction processing", "critical"),
        ("Your SSN {ssn} needs to be verified before we proceed.", "Pre-transaction check", "critical"),
        ("I can confirm your social {ssn} is correctly entered.", "Data validation", "critical"),
        ("Let me just verify - your SSN is {ssn}, correct?", "Double-checking information", "critical"),
        ("I'm seeing SSN {ssn} associated with this account.", "Account review", "critical"),
        ("Please confirm your full social security number: {ssn}.", "Requesting confirmation", "critical"),
        ("Your identification shows SSN {ssn} on our end.", "ID verification", "critical"),
    ]
    
    cases = []
    for template, context, severity in templates:
        ssn = random.choice(ssn_formats)
        last4 = ssn[-4:] if "-" not in ssn else ssn.split("-")[-1]
        cases.append({
            "policy_id": "PII-SSN",
            "agent_draft": template.format(ssn=ssn, last4=last4),
            "context": context,
            "severity": severity
        })
    
    return cases

def generate_disclosure_cases() -> List[Dict]:
    """Generate DISC-1.1 violation cases (missing required disclosures)."""
    templates = [
        ("Our fund has consistently delivered {percent}% returns over the past five years.", "Historical performance discussion", "medium"),
        ("You can expect solid returns based on our proven track record.", "Setting expectations", "medium"),
        ("This investment strategy has shown excellent growth historically.", "Strategy explanation", "medium"),
        ("Our clients typically see {percent}% annual gains on average.", "Average performance sharing", "medium"),
        ("The portfolio has performed exceptionally well with minimal volatility.", "Portfolio review", "medium"),
        ("Historically, this fund has outperformed the S&P 500 by {percent}%.", "Benchmark comparison", "medium"),
        ("You should see positive returns within 12-18 months based on trends.", "Timeline projection", "medium"),
        ("Our investment approach yields strong, consistent returns.", "Methodology explanation", "medium"),
        ("Past data shows this strategy works well in all market conditions.", "Market discussion", "medium"),
        ("This allocation has produced {percent}% average annual returns.", "Asset allocation review", "medium"),
        ("You'll likely see significant growth over the next few years.", "Long-term outlook", "medium"),
        ("The numbers show excellent performance across the board.", "Performance review", "medium"),
        ("Investors in this fund have enjoyed steady appreciation.", "Fund discussion", "medium"),
        ("This has been our best-performing product with {percent}% returns.", "Product recommendation", "medium"),
        ("You can expect similar results based on historical patterns.", "Pattern analysis", "medium"),
        ("The risk is low and the potential gains are substantial.", "Risk-reward discussion", "medium"),
        ("This conservative strategy still delivers {percent}% annually.", "Conservative approach", "medium"),
        ("Our track record speaks for itself - consistent profitability.", "Track record discussion", "medium"),
        ("You're looking at strong returns with this diversified approach.", "Diversification benefits", "medium"),
        ("The data clearly shows upward trends and positive outcomes.", "Data analysis", "medium"),
    ]
    
    cases = []
    percents = [6, 8, 10, 12, 15, 18]
    
    for template, context, severity in templates:
        if "{percent}" in template:
            pct = random.choice(percents)
            cases.append({
                "policy_id": "DISC-1.1",
                "agent_draft": template.format(percent=pct),
                "context": context,
                "severity": severity
            })
        else:
            cases.append({
                "policy_id": "DISC-1.1",
                "agent_draft": template,
                "context": context,
                "severity": severity
            })
    
    return cases

def generate_tone_cases() -> List[Dict]:
    """Generate TONE violation cases (inappropriate language)."""
    templates = [
        ("Don't be an idiot - just follow the simple instructions I gave you.", "Customer struggling with process", "low"),
        ("This is such a stupid question, I've already explained it twice.", "Customer asking for clarification", "low"),
        ("Stop being so dumb about this, it's really straightforward.", "Customer confused", "low"),
        ("Are you really that stupid? Let me spell it out for you.", "Customer making mistake", "low"),
        ("Just shut up and listen to what I'm telling you.", "Customer interrupting", "low"),
        ("Shut up for a second and let me finish explaining.", "Trying to explain", "low"),
        ("You'd have to be an idiot not to understand this concept.", "Teaching moment", "low"),
        ("What kind of stupid approach is that? That makes no sense.", "Customer's strategy discussion", "low"),
        ("Only idiots make that kind of mistake with their investments.", "Reviewing error", "low"),
        ("This is idiotic - you should have known better.", "Post-mistake discussion", "low"),
        ("Stop asking stupid questions and just do what I say.", "Customer seeking guidance", "low"),
        ("Seriously? That's the dumbest thing I've heard all day.", "Customer suggestion", "low"),
        ("You're being ridiculous and stupid about this whole situation.", "Disagreement", "low"),
        ("Just shut your mouth and let me help you properly.", "Customer talking over agent", "low"),
        ("What an idiotic way to handle your finances.", "Reviewing customer decisions", "low"),
        ("Don't be stupid - everyone knows you should diversify.", "Basic advice", "low"),
        ("That's a really dumb question that you should already know.", "Customer asking basics", "low"),
        ("Shut up about the fees and focus on the returns.", "Fee discussion", "low"),
        ("You're acting like an idiot - this is standard procedure.", "Customer questioning process", "low"),
        ("This stupid platform is so easy to use, I don't understand your problem.", "Technical support", "low"),
    ]
    
    return [
        {
            "policy_id": "TONE",
            "agent_draft": template,
            "context": context,
            "severity": severity
        }
        for template, context, severity in templates
    ]

def generate_multi_violation_cases() -> List[Dict]:
    """Generate cases with multiple policy violations."""
    cases = [
        # ADV-6.2 + DISC-1.1
        {
            "policy_id": "ADV-6.2,DISC-1.1",
            "agent_draft": "We guarantee 20% returns based on our five-year track record of consistent growth.",
            "context": "Sales pitch combining guarantee with historical data",
            "severity": "high"
        },
        {
            "policy_id": "ADV-6.2,DISC-1.1",
            "agent_draft": "This strategy guarantees profits - just look at our 15% average annual returns.",
            "context": "Persuasive pitch using past performance",
            "severity": "high"
        },
        {
            "policy_id": "ADV-6.2,DISC-1.1",
            "agent_draft": "I can guarantee similar results to our historical 18% yearly gains.",
            "context": "Setting expectations based on history",
            "severity": "high"
        },
        
        # ADV-6.2 + TONE
        {
            "policy_id": "ADV-6.2,TONE",
            "agent_draft": "Don't be stupid - obviously we guarantee returns on this investment.",
            "context": "Customer questioning guarantee claims",
            "severity": "high"
        },
        {
            "policy_id": "ADV-6.2,TONE",
            "agent_draft": "Shut up and listen - I'm guaranteeing you'll make money here.",
            "context": "Aggressive sales approach",
            "severity": "high"
        },
        {
            "policy_id": "ADV-6.2,TONE",
            "agent_draft": "Only an idiot would pass up these guaranteed risk-free returns.",
            "context": "Pressuring hesitant customer",
            "severity": "high"
        },
        
        # TONE + DISC-1.1
        {
            "policy_id": "TONE,DISC-1.1",
            "agent_draft": "Just shut up and look at our amazing 20% historical returns.",
            "context": "Performance discussion with inappropriate tone",
            "severity": "medium"
        },
        {
            "policy_id": "TONE,DISC-1.1",
            "agent_draft": "Stop being stupid - the data clearly shows 15% average gains.",
            "context": "Customer questioning performance claims",
            "severity": "medium"
        },
        {
            "policy_id": "TONE,DISC-1.1",
            "agent_draft": "Don't be an idiot - we've delivered 12% returns consistently for years.",
            "context": "Defending track record",
            "severity": "medium"
        },
        
        # Triple violations
        {
            "policy_id": "ADV-6.2,DISC-1.1,TONE",
            "agent_draft": "You'd be stupid not to take these guaranteed 18% returns we've consistently delivered.",
            "context": "High-pressure sales with multiple violations",
            "severity": "high"
        },
        {
            "policy_id": "ADV-6.2,DISC-1.1,TONE",
            "agent_draft": "Shut up and invest - we guarantee you'll see the same 15% we've always delivered.",
            "context": "Aggressive pitch combining violations",
            "severity": "high"
        },
        
        # PII + other violations
        {
            "policy_id": "PII-SSN,ADV-6.2",
            "agent_draft": "I found your SSN 123-45-6789 and can guarantee great returns on your account.",
            "context": "Security breach during sales pitch",
            "severity": "critical"
        },
        {
            "policy_id": "PII-SSN,TONE",
            "agent_draft": "Stop being stupid - your SSN 987-65-4321 is right here in the system.",
            "context": "Frustrated agent revealing PII",
            "severity": "critical"
        },
    ]
    
    return cases

def generate_clean_cases() -> List[Dict]:
    """Generate compliant (clean) cases."""
    templates = [
        # Proper disclaimers
        ("Past performance isn't indicative of future results, but I can share our historical track record if you'd like.", "Performance discussion", "none"),
        ("Investments carry risk and may lose value. Let's discuss your risk tolerance and goals.", "Risk assessment", "none"),
        ("While we can't guarantee returns, I can walk you through our investment strategy and associated risks.", "Strategy explanation", "none"),
        ("This investment involves risk, including potential loss of principal. Would you like to review the risk factors?", "Risk disclosure", "none"),
        
        # Helpful responses
        ("Let me provide you with the relevant information to help you make an informed decision.", "General inquiry", "none"),
        ("I understand your concern. Let me explain the details so you can decide what's best for you.", "Addressing concerns", "none"),
        ("That's a great question. Let me clarify the process for you.", "Customer inquiry", "none"),
        ("I appreciate your patience while I look into this for you.", "Research request", "none"),
        ("Let me walk you through the options and their respective risk profiles.", "Options discussion", "none"),
        ("I'm happy to explain our fee structure and how it compares to industry standards.", "Fee inquiry", "none"),
        
        # Professional service
        ("Thank you for bringing this to my attention. Let me investigate and get back to you.", "Issue reported", "none"),
        ("I understand this can be confusing. Let me break it down step by step.", "Complex topic", "none"),
        ("Your concern is valid. Let's review your account details together.", "Account review", "none"),
        ("I'm here to help you understand all aspects of this decision.", "Decision support", "none"),
        ("Let me provide you with the documentation so you can review it at your convenience.", "Information request", "none"),
        
        # Proper handling of sensitive info
        ("For your security, I'll verify your identity using the last four digits only.", "Verification", "none"),
        ("Let me access your account using secure authentication methods.", "Account access", "none"),
        ("I'll need to verify some information, but I won't ask for your full SSN over the phone.", "Security protocols", "none"),
        
        # Educational responses
        ("Let me explain how diversification can help manage risk in your portfolio.", "Education", "none"),
        ("I can share information about different asset classes and their characteristics.", "Investment education", "none"),
        ("Would you like me to explain how market volatility affects different investment types?", "Market education", "none"),
        
        # Proper expectations
        ("Returns vary based on market conditions and individual holdings. Let's review your specific situation.", "Performance discussion", "none"),
        ("There are no guarantees in investing, but I can help you understand the potential scenarios.", "Risk discussion", "none"),
        ("While past results show trends, future outcomes depend on many factors we can discuss.", "Historical analysis", "none"),
        
        # Customer service excellence
        ("I appreciate your feedback on this matter. How else can I assist you today?", "Closing conversation", "none"),
        ("Thank you for your patience. Is there anything else you'd like to know?", "Follow-up", "none"),
        ("I'm glad I could help clarify this for you. Please don't hesitate to reach out with more questions.", "Wrapping up", "none"),
        ("Let me summarize what we've discussed to ensure we're on the same page.", "Confirmation", "none"),
        ("I value your trust and want to ensure you have all the information you need.", "Building relationship", "none"),
        
        # Proper product discussion
        ("This product has specific features and limitations that I should explain.", "Product details", "none"),
        ("Let's review the prospectus together so you understand all aspects.", "Document review", "none"),
        ("I can compare different options and their characteristics to help you decide.", "Comparison", "none"),
        
        # Compliance-conscious language
        ("I'm required to disclose that all investments involve risk, including loss of principal.", "Required disclosure", "none"),
        ("Before we proceed, I need to ensure this aligns with your investment objectives.", "Suitability check", "none"),
        ("Let me provide you with all required disclosures for this product.", "Disclosure delivery", "none"),
        
        # Problem resolution
        ("I apologize for the confusion. Let me correct that information for you.", "Error correction", "none"),
        ("Thank you for your patience as we work through this issue together.", "Issue resolution", "none"),
        ("I'll make sure this gets resolved properly. Here's what I'll do next.", "Action plan", "none"),
        
        # Transparency
        ("I want to be transparent about the fees associated with this service.", "Fee disclosure", "none"),
        ("Let me explain exactly how this process works from start to finish.", "Process explanation", "none"),
        ("I'll be upfront about both the potential benefits and risks involved.", "Balanced discussion", "none"),
        
        # Empathy
        ("I understand this is an important decision. Take your time to consider all factors.", "Decision support", "none"),
        ("I can see why that would concern you. Let's address it together.", "Addressing concerns", "none"),
        ("Your financial well-being is important. Let's make sure we get this right.", "Showing care", "none"),
        
        # Additional professional responses
        ("I'd be happy to schedule a follow-up call to discuss this in more detail.", "Scheduling", "none"),
        ("Let me connect you with a specialist who can provide more specific guidance.", "Referral", "none"),
        ("I'll send you the materials so you can review them at your own pace.", "Documentation", "none"),
        ("Would it be helpful if I walked through a hypothetical scenario to illustrate this?", "Teaching approach", "none"),
        ("I'm here to answer any questions you have about this process.", "Open support", "none"),
    ]
    
    return [
        {
            "policy_id": "CLEAN",
            "agent_draft": template,
            "context": context,
            "severity": severity
        }
        for template, context, severity in templates
    ]

def main():
    """Generate synthetic coach cases."""
    print("Generating synthetic coach cases...")
    
    cases = []
    
    # Generate different case types
    cases.extend(generate_adv_cases())
    cases.extend(generate_pii_cases())
    cases.extend(generate_disclosure_cases())
    cases.extend(generate_tone_cases())
    cases.extend(generate_multi_violation_cases())
    cases.extend(generate_clean_cases())
    
    # Shuffle to mix case types
    random.shuffle(cases)
    
    # Ensure we have at least 250 cases
    while len(cases) < 250:
        # Add more variations by duplicating and modifying
        additional = random.choice([
            generate_adv_cases(),
            generate_disclosure_cases(),
            generate_clean_cases()
        ])
        cases.extend(random.sample(additional, min(10, 250 - len(cases))))
    
    # Write to file
    ensure_data_dir()
    output_path = "data/synthetic/coach_cases.jsonl"
    
    with open(output_path, "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")
    
    # Print summary
    print(f"\n✓ Generated {len(cases)} synthetic coach cases")
    print(f"✓ Saved to: {output_path}")
    
    # Breakdown by policy
    policy_counts = {}
    for case in cases:
        policy_id = case["policy_id"]
        policy_counts[policy_id] = policy_counts.get(policy_id, 0) + 1
    
    print("\nBreakdown by policy:")
    for policy_id in sorted(policy_counts.keys()):
        count = policy_counts[policy_id]
        print(f"  {policy_id}: {count} cases")
    
    # Breakdown by severity
    severity_counts = {}
    for case in cases:
        severity = case["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print("\nBreakdown by severity:")
    for severity in sorted(severity_counts.keys()):
        count = severity_counts[severity]
        print(f"  {severity}: {count} cases")
    
    print("\n✓ Seed data generation complete!")

if __name__ == "__main__":
    main()