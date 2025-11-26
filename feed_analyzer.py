#!/usr/bin/env python3
"""
XML Feed Analyzer
Analyzes XML feeds to search for information about jobs and teams
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import xml.etree.ElementTree as ET

# Tag mappings for field extraction (improves performance by avoiding repeated string definitions)
FIELD_TAGS = {
    'job_id': ('jobId', 'job-id', 'id', 'JobID', 'ID', 'requisitionId'),
    'reference_id': ('referenceId', 'reference-id', 'refId', 'ref-id', 'ReferenceID', 'refNumber', 'requisitionNumber'),
    'partner_job_id': ('partnerJobId', 'partner-job-id', 'PartnerJobId', 'partnerjobid'),
    'job_name': ('title', 'jobTitle', 'job-title', 'name', 'jobName', 'position', 'positionTitle', 'Title'),
    'company_id': ('companyId', 'company-id', 'clientId', 'client-id', 'CompanyID', 'teamId', 'team-id'),
    'company_name': ('company', 'companyName', 'company-name', 'client', 'clientName', 'Company', 'employer', 'organization', 'teamName'),
    'team_identifier': ('team', 'department', 'division', 'businessUnit', 'Team', 'Department'),
}

JOB_ELEMENT_TAGS = ('job', 'Job', 'position', 'Position', 'vacancy', 'Vacancy', 'requisition', 'Requisition', 'posting')

# Output width for table formatting
TABLE_WIDTH = 100


@dataclass
class JobInfo:
    """Information about a found job"""
    file: str
    job_id: Optional[str] = None
    reference_id: Optional[str] = None
    job_name: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    team_identifier: Optional[str] = None
    partner_job_id: Optional[str] = None
    xml_element: Optional[ET.Element] = None
    
    def matches_team(self, team_search: str) -> bool:
        """Checks if the job belongs to the searched team (case-insensitive)"""
        team_search_lower = team_search.lower()
        
        # Check all team/company related fields
        team_fields = (self.company_id, self.company_name, self.team_identifier)
        return any(field and team_search_lower in field.lower() for field in team_fields)
    
    def matches_job(self, job_search: str) -> bool:
        """Checks if it's the searched job (case-insensitive)"""
        job_search_lower = job_search.lower()
        
        # Check standard job fields
        job_fields = (self.job_id, self.reference_id, self.job_name)
        if any(field and job_search_lower in field.lower() for field in job_fields):
            return True
        
        # Check partner_job_id with special matching logic
        if self.partner_job_id:
            partner_clean = self.partner_job_id.replace(' ', '').lower()
            search_clean = job_search.replace(' ', '').lower()
            
            return (search_clean == partner_clean or 
                    search_clean in partner_clean or 
                    partner_clean.endswith(search_clean))
        
        return False
    
    def to_dict(self) -> Dict[str, str]:
        """Converts to dictionary for display"""
        return {
            'File': self.file,
            'Job ID': self.job_id or 'N/A',
            'Reference ID': self.reference_id or 'N/A',
            'Partner Job ID': self.partner_job_id or 'N/A',
            'Job Name': self.job_name or 'N/A',
            'Company ID': self.company_id or 'N/A',
            'Company Name': self.company_name or 'N/A',
            'Team Identifier': self.team_identifier or 'N/A'
        }


class FeedAnalyzer:
    """XML Feed Analyzer - Extracts job information from XML feeds"""
    
    def __init__(self, feeds_directory: str = "XMLFEEDS"):
        self.feeds_directory = Path(feeds_directory)
        if not self.feeds_directory.exists():
            self.feeds_directory.mkdir(parents=True, exist_ok=True)
        self._all_jobs_cache: Optional[List[JobInfo]] = None
    
    def _extract_text(self, element: ET.Element, *tags: str) -> Optional[str]:
        """Extracts text from an XML element searching through multiple possible tags"""
        for tag in tags:
            # Search with and without namespace
            for path in (f".//{tag}", f".//{{*}}{tag}"):
                found = element.find(path)
                if found is not None and found.text:
                    return found.text.strip()
        return None
    
    def _extract_partner_job_id(self, element: ET.Element) -> Optional[str]:
        """Extracts the partnerJobId which may contain CDATA"""
        for tag in FIELD_TAGS['partner_job_id']:
            for path in (f".//{tag}", f".//{{*}}{tag}"):
                found = element.find(path)
                if found is not None and found.text:
                    text = found.text.strip()
                    if text:
                        return text
        return None
    
    def _parse_job_from_element(self, element: ET.Element, filename: str) -> JobInfo:
        """Extracts job information from an XML element"""
        job = JobInfo(file=filename)
        
        # Extract all fields using tag mappings
        job.job_id = self._extract_text(element, *FIELD_TAGS['job_id'])
        job.reference_id = self._extract_text(element, *FIELD_TAGS['reference_id'])
        job.partner_job_id = self._extract_partner_job_id(element)
        job.job_name = self._extract_text(element, *FIELD_TAGS['job_name'])
        job.company_id = self._extract_text(element, *FIELD_TAGS['company_id'])
        job.company_name = self._extract_text(element, *FIELD_TAGS['company_name'])
        job.team_identifier = self._extract_text(element, *FIELD_TAGS['team_identifier'])
        job.xml_element = element
        
        return job
    
    def _parse_xml_file(self, filepath: Path) -> List[JobInfo]:
        """Parses an XML file and extracts all jobs"""
        jobs = []
        
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Collect all job elements from different tag names
            found_jobs = set()
            for tag in JOB_ELEMENT_TAGS:
                for path in (f".//{tag}", f".//{{*}}{tag}"):
                    for element in root.findall(path):
                        # Use element's memory address to avoid duplicates
                        elem_id = id(element)
                        if elem_id not in found_jobs:
                            found_jobs.add(elem_id)
                            job = self._parse_job_from_element(element, filepath.name)
                            jobs.append(job)
            
            # If no jobs found with common tags, try with root element
            if not jobs and root.tag:
                job = self._parse_job_from_element(root, filepath.name)
                if any([job.job_id, job.reference_id, job.job_name]):
                    jobs.append(job)
        
        except ET.ParseError as e:
            print(f"⚠️  Error parsing {filepath.name}: {e}")
        except Exception as e:
            print(f"⚠️  Error processing {filepath.name}: {e}")
        
        return jobs
    
    def analyze_all_feeds(self) -> List[JobInfo]:
        """Analyzes all XML files in the folder"""
        # Return cached results if available
        if self._all_jobs_cache is not None:
            return self._all_jobs_cache
        
        all_jobs = []
        xml_files = sorted(self.feeds_directory.glob("*.xml"))  # Sort for consistent output
        
        if not xml_files:
            print(f"⚠️  No XML files found in {self.feeds_directory}")
            return all_jobs
        
        total_files = len(xml_files)
        print(f"📁 Analyzing {total_files} XML file(s)...\n")
        
        for index, xml_file in enumerate(xml_files, 1):
            jobs = self._parse_xml_file(xml_file)
            all_jobs.extend(jobs)
            
            # Calculate progress
            percentage = (index / total_files) * 100
            remaining = total_files - index
            
            print(f"   [{percentage:5.1f}%] ✓ {xml_file.name}: {len(jobs)} job(s) found | {remaining} file(s) remaining")
        
        print(f"\n📊 Total: {len(all_jobs)} job(s) in {total_files} file(s)\n")
        
        # Cache results
        self._all_jobs_cache = all_jobs
        return all_jobs
    
    def search_jobs_by_team(self, team_identifier: str) -> List[JobInfo]:
        """Searches for all jobs from a specific team"""
        all_jobs = self.analyze_all_feeds()
        matching_jobs = [job for job in all_jobs if job.matches_team(team_identifier)]
        
        print(f"🔍 Search: Jobs from team '{team_identifier}'")
        print(f"📊 Results: {len(matching_jobs)} job(s) found\n")
        
        return matching_jobs
    
    def search_specific_job(self, team_identifier: str, job_identifier: str) -> List[JobInfo]:
        """Searches for a specific job from a specific team"""
        all_jobs = self.analyze_all_feeds()
        matching_jobs = [
            job for job in all_jobs 
            if job.matches_team(team_identifier) and job.matches_job(job_identifier)
        ]
        
        print(f"🔍 Search: Job '{job_identifier}' from team '{team_identifier}'")
        print(f"📊 Results: {len(matching_jobs)} job(s) found\n")
        
        return matching_jobs
    
    def get_summary_by_team(self) -> Dict[str, int]:
        """Gets a summary of jobs grouped by team"""
        all_jobs = self.analyze_all_feeds()
        summary = defaultdict(int)
        
        for job in all_jobs:
            # Use the first available identifier as key
            team_key = (job.company_name or 
                       job.company_id or 
                       job.team_identifier or 
                       "Unknown Team")
            summary[team_key] += 1
        
        return dict(summary)


def print_jobs_table(jobs: List[JobInfo]) -> None:
    """Prints jobs in a formatted table"""
    if not jobs:
        print("No jobs found.")
        return
    
    print("=" * TABLE_WIDTH)
    for i, job in enumerate(jobs, 1):
        print(f"\n🔹 Job #{i}")
        print(f"   File:           {job.file}")
        print(f"   Job ID:         {job.job_id or 'N/A'}")
        print(f"   Partner Job ID: {job.partner_job_id or 'N/A'}")
        print(f"   Reference ID:   {job.reference_id or 'N/A'}")
        print(f"   Job Name:       {job.job_name or 'N/A'}")
        print(f"   Company Name:   {job.company_name or 'N/A'}")
        print(f"   Company ID:     {job.company_id or 'N/A'}")
        if job.team_identifier:
            print(f"   Team:           {job.team_identifier}")
    print("\n" + "=" * TABLE_WIDTH)


def print_usage() -> None:
    """Prints usage information"""
    print("📋 XML Feed Analyzer - Usage:")
    print("\n  Option 1: Search all jobs from a team")
    print("    python feed_analyzer.py team <team_identifier>")
    print("\n  Option 2: Search a specific job from a team")
    print("    python feed_analyzer.py job <team_identifier> <job_identifier>")
    print("\n  Option 3: View summary by teams")
    print("    python feed_analyzer.py summary")
    print("\n  Option 4: List all jobs")
    print("    python feed_analyzer.py all")
    print("\nExamples:")
    print("  python feed_analyzer.py team 'Acme Corp'")
    print("  python feed_analyzer.py job 'Acme Corp' 'Senior Developer'")
    print("  python feed_analyzer.py summary")


def main() -> None:
    """Main function for command-line interface"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    analyzer = FeedAnalyzer("XMLFEEDS")
    command = sys.argv[1].lower()
    
    if command == "team" and len(sys.argv) >= 3:
        jobs = analyzer.search_jobs_by_team(sys.argv[2])
        print_jobs_table(jobs)
    
    elif command == "job" and len(sys.argv) >= 4:
        jobs = analyzer.search_specific_job(sys.argv[2], sys.argv[3])
        print_jobs_table(jobs)
    
    elif command == "summary":
        summary = analyzer.get_summary_by_team()
        print("📊 Job Summary by Team:\n")
        for team, count in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"   {team}: {count} job(s)")
    
    elif command == "all":
        jobs = analyzer.analyze_all_feeds()
        print_jobs_table(jobs)
    
    else:
        print("❌ Unrecognized command. Use: team, job, summary, or all")


if __name__ == "__main__":
    main()
