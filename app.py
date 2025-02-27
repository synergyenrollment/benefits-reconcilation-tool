# Main application pages based on app stage
if st.session_state.app_stage == 'upload':
    st.markdown('<div class="section-header">Upload Files</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">Select the appropriate scenario based on your data sources.</div>', unsafe_allow_html=True)
    
    # Scenario selection
    scenario = st.radio(
        "Select Reconciliation Scenario:",
        ["Brand New Group (No Previous Data)", 
         "Existing Group: Compare Current & Previous"],
        index=0,
        key="scenario_selection"
    )
    
    # File upload section based on scenario
    st.markdown('<div class="section-header">Upload Files</div>', unsafe_allow_html=True)
    
    if scenario == "Brand New Group (No Previous Data)":
        st.markdown("For new groups with no previous data, upload only the current enrollment report or invoice.")
        current_file = st.file_uploader("Upload Current Enrollment/Invoice:", 
                                        type=["csv", "xlsx", "xls", "pdf"],
                                        key="new_group_file")
        
        if current_file:
            try:
                # Initialize the reconciliation engine
                reconciliation = BenefitReconciliation()
                
                # Load and process the file
                with st.spinner("Processing file..."):
                    df = reconciliation.load_file(current_file)
                    file_type = reconciliation.identify_file_type(df)
                    std_data = reconciliation.standardize_data(df, file_type)
                    
                    # Store the data
                    st.session_state.current_data = std_data
                    st.session_state.previous_data = None
                    
                    # Show success message
                    st.markdown('<div class="success-box">File processed successfully! You can now preview the data.</div>', unsafe_allow_html=True)
                    
                    # Button to proceed
                    if st.button("Preview Data", key="preview_new_group"):
                        st.session_state.app_stage = 'preview'
                        st.experimental_rerun()
            
            except Exception as e:
                st.markdown(f'<div class="error-box">Error processing file: {str(e)}</div>', unsafe_allow_html=True)
    
    else:  # Existing Group scenario
        st.markdown("For existing groups, upload both current and previous data sources.")
        
        col1, col2 = st.columns(2)
        with col1:
            current_file = st.file_uploader("Upload Current Enrollment/Invoice:", 
                                           type=["csv", "xlsx", "xls", "pdf"],
                                           key="existing_current_file")
        
        with col2:
            previous_file = st.file_uploader("Upload Previous Enrollment/Invoice:", 
                                            type=["csv", "xlsx", "xls", "pdf"],
                                            key="existing_previous_file")
        
        if current_file and previous_file:
            try:
                # Initialize the reconciliation engine
                reconciliation = BenefitReconciliation()
                
                # Process both files
                with st.spinner("Processing files..."):
                    # Current file
                    current_df = reconciliation.load_file(current_file)
                    current_type = reconciliation.identify_file_type(current_df)
                    current_std = reconciliation.standardize_data(current_df, current_type)
                    
                    # Previous file
                    previous_df = reconciliation.load_file(previous_file)
                    previous_type = reconciliation.identify_file_type(previous_df)
                    previous_std = reconciliation.standardize_data(previous_df, previous_type)
                    
                    # Store the data
                    st.session_state.current_data = current_std
                    st.session_state.previous_data = previous_std
                    
                    # Show success message
                    st.markdown('<div class="success-box">Files processed successfully! You can now preview the data.</div>', unsafe_allow_html=True)
                    
                    # Button to proceed
                    if st.button("Preview Data", key="preview_existing_group"):
                        st.session_state.app_stage = 'preview'
                        st.experimental_rerun()
            
            except Exception as e:
                st.markdown(f'<div class="error-box">Error processing files: {str(e)}</div>', unsafe_allow_html=True)

elif st.session_state.app_stage == 'preview':
    st.markdown('<div class="section-header">Data Preview</div>', unsafe_allow_html=True)
    
    # Create tabs for current and previous data
    tab1, tab2 = st.tabs(["Current Data", "Previous Data"])
    
    with tab1:
        if st.session_state.current_data is not None:
            st.markdown(f"### Current Data ({len(st.session_state.current_data)} records)")
            st.dataframe(st.session_state.current_data.head(100))
            
            if len(st.session_state.current_data) > 100:
                st.info(f"Showing first 100 of {len(st.session_state.current_data)} records")
            
            # Column information
            st.markdown("### Column Information")
            cols = st.session_state.current_data.columns.tolist()
            required_cols = ['policy_id', 'product', 'premium']
            
            for col in required_cols:
                if col in cols:
                    st.markdown(f"✅ **{col}** - Found and will be used for reconciliation")
                else:
                    st.markdown(f"❌ **{col}** - Not found! This is required for reconciliation")
            
            # Optional columns for enhanced matching
            st.markdown("#### Optional Columns for Enhanced Matching")
            optional_cols = ['first_name', 'last_name', 'ssn_last4', 'full_name']
            found_optional = [col for col in optional_cols if col in cols]
            
            if found_optional:
                for col in found_optional:
                    st.markdown(f"✅ **{col}** - Found and will be used for enhanced policy matching")
            else:
                st.markdown("❌ No columns found for enhanced matching. Only policy ID matching will be used.")
    
    with tab2:
        if st.session_state.previous_data is not None:
            st.markdown(f"### Previous Data ({len(st.session_state.previous_data)} records)")
            st.dataframe(st.session_state.previous_data.head(100))
            
            if len(st.session_state.previous_data) > 100:
                st.info(f"Showing first 100 of {len(st.session_state.previous_data)} records")
            
            # Column information for matching
            st.markdown("### Column Information for Matching")
            prev_cols = st.session_state.previous_data.columns.tolist()
            
            for col in required_cols:
                if col in prev_cols:
                    st.markdown(f"✅ **{col}** - Found in previous data")
                else:
                    st.markdown(f"❌ **{col}** - Not found in previous data! This may affect matching.")
            
            # Check for matching columns
            current_cols = st.session_state.current_data.columns.tolist()
            common_cols = set(current_cols).intersection(set(prev_cols))
            st.markdown(f"📊 **{len(common_cols)} common columns** between current and previous data")
        else:
            st.info("Brand new group - no previous data to display")
    
    # Buttons to proceed
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Configure Settings", key="goto_settings"):
            st.session_state.app_stage = 'settings'
            st.experimental_rerun()
    with col2:
        if st.button("Return to Upload", key="back_to_upload"):
            st.session_state.app_stage = 'upload'
            st.experimental_rerun()

elif st.session_state.app_stage == 'settings':
    st.markdown('<div class="section-header">Configuration Settings</div>', unsafe_allow_html=True)
    
    # Create tabs for different settings
    tab1, tab2, tab3 = st.tabs(["Commission Settings", "Matching Settings", "Run Reconciliation"])
    
    with tab1:
        st.markdown("### Commission Rates (Carrier Pays)")
        st.markdown("Set the commission rates for each product")
        
        # Get all unique products from the data
        all_products = []
        if st.session_state.current_data is not None:
            all_products = st.session_state.current_data['product'].dropna().unique().tolist()
        
        # Ensure the default products are always included
        default_products = ['Accident', 'Critical Illness', 'Hospital Indemnity', 
                           'Cancer', 'Short Term Disability', 'Life', 'default']
        for product in default_products:
            if product not in all_products:
                all_products.append(product)
        
        # Display commission rate inputs for each product
        commission_rates = {}
        for product in all_products:
            st.markdown(f"#### {product}")
            col1, col2 = st.columns(2)
            
            with col1:
                new_rate = st.number_input(
                    f"New Business Rate ({product})",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.commission_settings['rates'].get(
                        product, {'new': 0.15, 'renewal': 0.05})['new'],
                    format="%.3f",
                    step=0.001,
                    key=f"new_rate_{product}"
                )
            
            with col2:
                renewal_rate = st.number_input(
                    f"Renewal Rate ({product})",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.commission_settings['rates'].get(
                        product, {'new': 0.15, 'renewal': 0.05})['renewal'],
                    format="%.3f",
                    step=0.001,
                    key=f"renewal_rate_{product}"
                )
            
            commission_rates[product] = {'new': new_rate, 'renewal': renewal_rate}
        
        st.markdown("### Commission Splits (Your Firm's Percentage)")
        st.markdown("Set your firm's percentage of the total commission")
        
        # Display commission split inputs for each product
        commission_splits = {}
        for product in all_products:
            split = st.slider(
                f"Split Percentage for {product}",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.commission_settings['splits'].get(product, 0.5),
                format="%.2f",
                step=0.01,
                key=f"split_{product}"
            )
            commission_splits[product] = split
        
        # Save commission settings button
        if st.button("Save Commission Settings", key="save_commission"):
            st.session_state.commission_settings = {
                'rates': commission_rates,
                'splits': commission_splits
            }
            st.success("Commission settings saved successfully!")
    
    with tab2:
        st.markdown("### Policy Matching Configuration")
        st.markdown("Configure how policies are matched between current and previous data")
        
        # Matching method selection
        st.markdown("#### Select Matching Methods")
        use_policy_id = st.checkbox(
            "Match by Policy ID + Product (Highest Confidence)",
            value=st.session_state.matching_settings['use_policy_id'],
            key="use_policy_id"
        )
        
        use_ssn = st.checkbox(
            "Match by SSN Last 4 + Product (High Confidence)",
            value=st.session_state.matching_settings['use_ssn'],
            key="use_ssn"
        )
        
        use_name = st.checkbox(
            "Match by Employee Name + Product (Medium Confidence)",
            value=st.session_state.matching_settings['use_name'],
            key="use_name"
        )
        
        # Confidence threshold
        st.markdown("#### Match Confidence Threshold")
        confidence_threshold = st.slider(
            "Minimum confidence to consider a match valid",
            min_value=0.5,
            max_value=1.0,
            value=st.session_state.matching_settings['confidence_threshold'],
            format="%.1f",
            step=0.1,
            key="confidence_threshold"
        )
        
        st.markdown("*Higher values reduce false matches but may miss some renewals*")
        
        # Fuzzy matching settings
        st.markdown("#### Fuzzy Name Matching")
        if HAVE_FUZZY:
            fuzzy_threshold = st.slider(
                "Name Similarity Threshold",
                min_value=70,
                max_value=100,
                value=st.session_state.matching_settings['fuzzy_threshold'],
                format="%d%%",
                step=5,
                key="fuzzy_threshold"
            )
        else:
            st.warning("Fuzzy matching library (fuzzywuzzy) not installed. For enhanced name matching, install it using: pip install fuzzywuzzy")
            fuzzy_threshold = st.session_state.matching_settings['fuzzy_threshold']
        
        # Save matching settings button
        if st.button("Save Matching Settings", key="save_matching"):
            st.session_state.matching_settings = {
                'use_policy_id': use_policy_id,
                'use_ssn': use_ssn,
                'use_name': use_name,
                'confidence_threshold': confidence_threshold,
                'fuzzy_threshold': fuzzy_threshold
            }
            st.success("Matching settings saved successfully!")
    
    with tab3:
        st.markdown("### Run Reconciliation")
        st.markdown("Process the data and generate revenue projections")
        
        # Summary of selected settings
        st.markdown("#### Selected Settings")
        
        # Commission settings summary
        with st.expander("Commission Settings Summary"):
            for product in all_products:
                st.markdown(f"**{product}**")
                rates = st.session_state.commission_settings['rates'].get(
                    product, {'new': 0.15, 'renewal': 0.05})
                split = st.session_state.commission_settings['splits'].get(product, 0.5)
                
                st.markdown(f"- New Business Rate: {rates['new']:.1%}")
                st.markdown(f"- Renewal Rate: {rates['renewal']:.1%}")
                st.markdown(f"- Your Split: {split:.0%}")
                st.markdown("---")
        
        # Matching settings summary
        with st.expander("Matching Settings Summary"):
            st.markdown(f"- Policy ID Matching: {'Enabled' if st.session_state.matching_settings['use_policy_id'] else 'Disabled'}")
            st.markdown(f"- SSN Last 4 Matching: {'Enabled' if st.session_state.matching_settings['use_ssn'] else 'Disabled'}")
            st.markdown(f"- Name Matching: {'Enabled' if st.session_state.matching_settings['use_name'] else 'Disabled'}")
            st.markdown(f"- Confidence Threshold: {st.session_state.matching_settings['confidence_threshold']:.1f}")
            st.markdown(f"- Fuzzy Threshold: {st.session_state.matching_settings['fuzzy_threshold']}%")
        
        # Button to run reconciliation
        if st.button("Run Reconciliation Now", key="run_reconciliation"):
            try:
                with st.spinner("Processing data and generating revenue projections..."):
                    # Initialize the reconciliation engine
                    reconciliation = BenefitReconciliation(
                        commission_splits=st.session_state.commission_settings['splits'],
                        default_split=st.session_state.commission_settings['splits']['default']
                    )
                    
                    # Apply matching settings
                    for key, value in st.session_state.matching_settings.items():
                        setattr(reconciliation, key, value)
                    
                    # Run appropriate scenario
                    if st.session_state.previous_data is None:
                        # Brand new group scenario
                        projections, summary = reconciliation.scenario_brand_new_group(
                            st.session_state.current_data,
                            commission_rates=st.session_state.commission_settings['rates'],
                            commission_splits=st.session_state.commission_settings['splits'],
                            default_split=st.session_state.commission_settings['splits']['default']
                        )
                    else:
                        # Existing group scenario
                        projections, summary = reconciliation.scenario_existing_group(
                            st.session_state.current_data,
                            st.session_state.previous_data,
                            matching_settings=st.session_state.matching_settings,
                            commission_rates=st.session_state.commission_settings['rates'],
                            commission_splits=st.session_state.commission_settings['splits'],
                            default_split=st.session_state.commission_settings['splits']['default']
                        )
                    
                    # Store results
                    st.session_state.results_data = projections
                    st.session_state.summary_data = summary
                    
                    # Update app stage to show results
                    st.session_state.app_stage = 'results'
                    st.success("Reconciliation completed successfully! View the results in the Results tab.")
                    st.experimental_rerun()
            
            except Exception as e:
                st.error(f"Error running reconciliation: {str(e)}")

elif st.session_state.app_stage == 'results':
    st.markdown('<div class="section-header">Reconciliation Results</div>', unsafe_allow_html=True)
    
    # Check if we have results
    if st.session_state.results_data is None or st.session_state.summary_data is None:
        st.warning("No reconciliation results to display. Please run reconciliation first.")
        
        if st.button("Go to Settings"):
            st.session_state.app_stage = 'settings'
            st.experimental_rerun()
    
    else:
        # Create tabs for summary and details
        tab1, tab2, tab3 = st.tabs(["Summary", "Detailed Projections", "Export Data"])
        
        with tab1:
            # Key metrics
            st.markdown("### Key Metrics")
            
            # Get summary data
            summary = st.session_state.summary_data
            
            # Row of key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Projected Revenue",
                    f"${summary['total_projected_revenue']:,.2f}"
                )
                
                st.metric(
                    "New Policies",
                    f"{summary['policy_counts'].get('new', 0):,}"
                )
            
            with col2:
                st.metric(
                    "New Business Revenue",
                    f"${summary['revenue_by_status'].get('new', 0):,.2f}"
                )
                
                st.metric(
                    "Renewal Policies",
                    f"{summary['policy_counts'].get('renewal', 0):,}"
                )
            
            with col3:
                st.metric(
                    "Renewal Revenue",
                    f"${summary['revenue_by_status'].get('renewal', 0):,.2f}"
                )
                
                st.metric(
                    "Avg. Revenue Per Policy",
                    f"${summary['avg_revenue_per_policy']:,.2f}"
                )
            
            # Match quality information
            if 'match_methods' in summary and 'confidence_counts' in summary:
                st.markdown("### Match Quality")
                
                # Confidence distribution chart
                confidence_counts = summary['confidence_counts']
                confidence_labels = ['very_high (0.9-1.0)', 'high (0.8-0.9)', 'medium (0.7-0.8)', 'low (<0.7)']
                
                # Filter out any levels that don't exist in the data
                confidence_labels = [label for label in confidence_labels if label in confidence_counts]
                
                if confidence_labels:
                    confidence_values = [confidence_counts.get(label, 0) for label in confidence_labels]
                    
                    # Create a DataFrame for the chart
                    chart_data = pd.DataFrame({
                        'Confidence Level': confidence_labels,
                        'Count': confidence_values
                    })
                    
                    # Plot confidence distribution
                    st.markdown("#### Renewal Policy Match Confidence")
                    st.bar_chart(chart_data.set_index('Confidence Level'))
                
                # Match methods breakdown
                st.markdown("#### Matching Methods Used")
                
                match_methods = summary['match_methods']
                method_names = []
                method_counts = []
                
                # Process match methods for display
                if 'policy_id' in match_methods:
                    method_names.append('Policy ID')
                    method_counts.append(match_methods['policy_id'])
                
                if 'ssn_last4' in match_methods:
                    method_names.append('SSN Last 4')
                    method_counts.append(match_methods['ssn_last4'])
                
                if 'name_exact' in match_methods:
                    method_names.append('Exact Name')
                    method_counts.append(match_methods['name_exact'])
                
                # Count fuzzy matches
                fuzzy_count = sum(count for method, count in match_methods.items() 
                                 if 'name_fuzzy' in method)
                if fuzzy_count > 0:
                    method_names.append('Fuzzy Name')
                    method_counts.append(fuzzy_count)
                
                # Create DataFrame for the chart
                if method_names:
                    methods_df = pd.DataFrame({
                        'Method': method_names,
                        'Count': method_counts
                    })
                    
                    # Plot methods chart
                    st.bar_chart(methods_df.set_index('Method'))
            
            # Revenue by product
            st.markdown("### Revenue by Product")
            
            # Create DataFrame for the chart
            product_revenue = []
            for product, revenue in summary['revenue_by_product'].items():
                product_revenue.append({
                    'Product': product,
                    'Revenue': revenue
                })
            
            product_df = pd.DataFrame(product_revenue)
            
            # Sort by revenue descending
            product_df = product_df.sort_values('Revenue', ascending=False)
            
            # Show chart and table
            st.bar_chart(product_df.set_index('Product'))
            
            # Table with formatted revenue
            display_df = product_df.copy()
            display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"${x:,.2f}")
            st.table(display_df)
        
        with tab2:
            # Detailed projections
            st.markdown("### Detailed Projections")
            
            # Get results data
            results = st.session_state.results_data
            
            # Filtering options
            st.markdown("#### Filter Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Filter by status
                status_filter = st.multiselect(
                    "Policy Status:",
                    options=results['policy_status'].unique(),
                    default=results['policy_status'].unique(),
                    key="status_filter"
                )
            
            with col2:
                # Filter by product
                product_filter = st.multiselect(
                    "Product:",
                    options=results['product'].unique(),
                    default=results['product'].unique(),
                    key="product_filter"
                )
            
            # Apply filters
            filtered_results = results[
                results['policy_status'].isin(status_filter) &
                results['product'].isin(product_filter)
            ]
            
            # Show filtering summary
            st.markdown(f"Showing {len(filtered_results):,} of {len(results):,} policies")
            
            # Color-code based on match confidence
            def highlight_confidence(row):
                if row['policy_status'] == 'renewal':
                    confidence = row['match_confidence']
                    if confidence >= 0.9:
                        return ['background-color: #d4edda'] * len(row)
                    elif confidence >= 0.8:
                        return ['background-color: #fff3cd'] * len(row)
                    else:
                        return ['background-color: #f8d7da'] * len(row)
                return [''] * len(row)
            
            # Format the DataFrame for display
            display_cols = ['policy_id', 'product', 'premium', 'policy_status', 
                           'match_method', 'match_confidence', 'commission_rate', 
                           'annual_premium', 'projected_revenue']
            
            display_df = filtered_results[display_cols].copy()
            
            # Format numeric columns
            display_df['premium'] = display_df['premium'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")
            display_df['commission_rate'] = display_df['commission_rate'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "")
            display_df['match_confidence'] = display_df['match_confidence'].apply(lambda x: f"{x:.2%}" if pd.notna(x) and x > 0 else "")
            display_df['annual_premium'] = display_df['annual_premium'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")
            display_df['projected_revenue'] = display_df['projected_revenue'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")
            
            # Show styled DataFrame
            st.dataframe(display_df.style.apply(highlight_confidence, axis=1), height=400)
        
        with tab3:
            # Export options
            st.markdown("### Export Results")
            st.markdown("Download the reconciliation results for further analysis")
            
            # Export format options
            export_format = st.radio(
                "Select Export Format:",
                ["Excel (.xlsx)", "CSV (.csv)"],
                key="export_format"
            )
            
            # What to include in export
            include_projections = st.checkbox("Include Detailed Projections", value=True, key="include_projections")
            include_summary = st.checkbox("Include Summary", value=True, key="include_summary")
            
            if st.button("Prepare Export File", key="prepare_export"):
                try:
                    with st.spinner("Preparing export file..."):
                        if export_format == "Excel (.xlsx)":
                            # Create Excel file in memory
                            buffer = BytesIO()
                            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                                # Detailed projections
                                if include_projections:
                                    st.session_state.results_data.to_excel(writer, sheet_name="Detailed Projections", index=False)
                                
                                # Summary information
                                if include_summary:
                                    # Convert summary to DataFrame
                                    summary = st.session_state.summary_data
                                    
                                    # Key metrics
                                    metrics_df = pd.DataFrame([
                                        {'Metric': 'Total Projected Revenue', 'Value': summary['total_projected_revenue']},
                                        {'Metric': 'New Business Revenue', 'Value': summary['revenue_by_status'].get('new', 0)},
                                        {'Metric': 'Renewal Revenue', 'Value': summary['revenue_by_status'].get('renewal', 0)},
                                        {'Metric': 'New Policies Count', 'Value': summary['policy_counts'].get('new', 0)},
                                        {'Metric': 'Renewal Policies Count', 'Value': summary['policy_counts'].get('renewal', 0)},
                                        {'Metric': 'Average Revenue Per Policy', 'Value': summary['avg_revenue_per_policy']}
                                    ])
                                    
                                    metrics_df.to_excel(writer, sheet_name="Summary", index=False)
                                    
                                    # Revenue by product
                                    product_df = pd.DataFrame([
                                        {'Product': product, 'Revenue': revenue}
                                        for product, revenue in summary['revenue_by_product'].items()
                                    ])
                                    
                                    product_df.to_excel(writer, sheet_name="Revenue by Product", index=False)
                                    
                                    # Match quality if available
                                    if 'match_methods' in summary and 'confidence_counts' in summary:
                                        # Match methods
                                        method_df = pd.DataFrame([
                                            {'Match Method': method, 'Count': count}
                                            for method, count in summary['match_methods'].items()
                                        ])
                                        
                                        method_df.to_excel(writer, sheet_name="Match Quality", index=False)
                                        
                                        # Confidence counts
                                        confidence_df = pd.DataFrame([
                                            {'Confidence Level': level, 'Count': count}
                                            for level, count in summary['confidence_counts'].items()
                                        ])
                                        
                                        confidence_df.to_excel(writer, sheet_name="Match Quality", 
                                                             startrow=len(method_df) + 3, index=False)
                            
                            # Generate download link
                            buffer.seek(0)
                            b64 = base64.b64encode(buffer.read()).decode()
                            filename = f"benefit_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="btn">Download Excel File</a>'
                            st.markdown(href, unsafe_allow_html=True)
                        
                        else:  # CSV format
                            # For CSV, we can only include one table, so we default to detailed projections
                            if include_projections:
                                csv = st.session_state.results_data.to_csv(index=False)
                                b64 = base64.b64encode(csv.encode()).decode()
                                filename = f"benefit_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                href = f'<a href="data:text/csv;base64,{b64}" download="{filename}" class="btn">Download CSV File</a>'
                                st.markdown(href, unsafe_allow_html=True)
                            else:
                                st.warning("Please select 'Include Detailed Projections' for CSV export")
                
                except Exception as e:
                    st.error(f"Error creating export file: {str(e)}")

# Add footer
st.markdown("---")
st.markdown("Benefits Enrollment Reconciliation Tool | Developed by Claude")

# Initialize with demo data option (for easier testing)
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    # Option to load demo data
    with st.sidebar:
        if st.button("Load Demo Data"):
            # Create sample data
            # Current data
            current_data = pd.DataFrame({
                'policy_id': [f"P{i:06d}" for i in range(1, 101)],
                'first_name': ['John', 'Jane', 'Robert', 'Mary', 'James'] * 20,
                'last_name': ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown'] * 20,
                'product': ['Accident', 'Critical Illness', 'Hospital Indemnity', 
                           'Cancer', 'Short Term Disability'] * 20,
                'premium': [50 + i * 0.5 for i in range(100)]
            })
            
            # Previous data - 75% the same, 25% different
            previous_data = pd.DataFrame({
                'policy_id': [f"P{i:06d}" for i in range(1, 76)] + [f"P{i+200:06d}" for i in range(76, 101)],
                'first_name': ['John', 'Jane', 'Robert', 'Mary', 'James'] * 20,
                'last_name': ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown'] * 20,
                'product': ['Accident', 'Critical Illness', 'Hospital Indemnity', 
                           'Cancer', 'Short Term Disability'] * 20,
                'premium': [45 + i * 0.5 for i in range(100)]
            })
            
            # Store in session state
            st.session_state.current_data = current_data
            st.session_state.previous_data = previous_data
            st.session_state.app_stage = 'preview'
            
            st.success("Demo data loaded successfully!")
            st.experimental_rerun()
import streamlit as st
import pandas as pd
import numpy as np
import base64
import io
from io import BytesIO
import re
from datetime import datetime
import tempfile
import os

# Import PDF processing libraries
try:
    import tabula
    import PyPDF2
    import pdfplumber
    HAVE_PDF_TOOLS = True
except ImportError:
    HAVE_PDF_TOOLS = False

# Import fuzzy matching library
try:
    from fuzzywuzzy import fuzz
    HAVE_FUZZY = True
except ImportError:
    HAVE_FUZZY = False

# Set page configuration
st.set_page_config(
    page_title="Benefits Reconciliation Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        margin-bottom: 1rem;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        color: #856404;
        margin-bottom: 1rem;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        margin-bottom: 1rem;
    }
    .confidence-high {
        background-color: #d4edda;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
    }
    .confidence-medium {
        background-color: #fff3cd;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
    }
    .confidence-low {
        background-color: #f8d7da;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
    }
    /* Style the tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        padding: 0 16px;
        gap: 1px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown('<div class="main-header">Benefits Enrollment Reconciliation Tool</div>', unsafe_allow_html=True)

# Define states for the application flow
if 'app_stage' not in st.session_state:
    st.session_state.app_stage = 'upload'  # Stages: upload, preview, settings, process, results

if 'current_data' not in st.session_state:
    st.session_state.current_data = None

if 'previous_data' not in st.session_state:
    st.session_state.previous_data = None

if 'results_data' not in st.session_state:
    st.session_state.results_data = None

if 'summary_data' not in st.session_state:
    st.session_state.summary_data = None

if 'commission_settings' not in st.session_state:
    # Default commission rates
    st.session_state.commission_settings = {
        'rates': {
            'Accident': {'new': 0.20, 'renewal': 0.05},
            'Critical Illness': {'new': 0.25, 'renewal': 0.07},
            'Hospital Indemnity': {'new': 0.20, 'renewal': 0.06},
            'Cancer': {'new': 0.18, 'renewal': 0.05},
            'Short Term Disability': {'new': 0.15, 'renewal': 0.05},
            'Life': {'new': 0.12, 'renewal': 0.04},
            'default': {'new': 0.15, 'renewal': 0.05}
        },
        'splits': {
            'Accident': 0.55,
            'Critical Illness': 0.50,
            'Hospital Indemnity': 0.60,
            'Cancer': 0.45,
            'Short Term Disability': 0.40,
            'Life': 0.50,
            'default': 0.50
        }
    }

if 'matching_settings' not in st.session_state:
    st.session_state.matching_settings = {
        'use_policy_id': True,
        'use_ssn': True,
        'use_name': True,
        'confidence_threshold': 0.7,
        'fuzzy_threshold': 85
    }

# Function to reset the application state
def reset_app():
    st.session_state.app_stage = 'upload'
    st.session_state.current_data = None
    st.session_state.previous_data = None
    st.session_state.results_data = None
    st.session_state.summary_data = None

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/cotton/64/000000/analytics.png", width=64)
    st.title("Navigation")
    
    # Only show navigation if we have data loaded
    if st.session_state.current_data is not None:
        nav = st.radio(
            "Go to:",
            ["Upload Files", "Data Preview", "Settings", "Results"],
            index=0 if st.session_state.app_stage == 'upload' else
                  1 if st.session_state.app_stage == 'preview' else
                  2 if st.session_state.app_stage == 'settings' else 3
        )
        
        if nav == "Upload Files":
            st.session_state.app_stage = 'upload'
        elif nav == "Data Preview":
            st.session_state.app_stage = 'preview'
        elif nav == "Settings":
            st.session_state.app_stage = 'settings'
        elif nav == "Results":
            st.session_state.app_stage = 'results'
    
    st.markdown("---")
    if st.button("Reset Application", key="reset_button"):
        reset_app()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool helps reconcile enrollment data and project revenue based on policy status (new vs. renewal).
    
    **Features:**
    - Multi-tier policy matching
    - PDF, Excel, and CSV support
    - Confidence scoring
    - Revenue projections
    """)

# Core functionality classes and functions
class BenefitReconciliation:
    """Core reconciliation engine"""
    
    def __init__(self, commission_splits=None, default_split=0.5):
        """Initialize the reconciliation tool"""
        self.commission_splits = commission_splits or {}
        self.default_split = default_split
        
        # Matching settings with defaults
        self.use_policy_id_matching = True
        self.use_ssn_matching = True
        self.use_name_matching = True
        self.confidence_threshold = 0.7
        self.fuzzy_threshold = 85
    
    def load_file(self, uploaded_file):
        """Load data from uploaded file"""
        # Get file extension
        file_name = uploaded_file.name
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Process based on file type
        if file_ext == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(uploaded_file)
        elif file_ext == '.pdf' and HAVE_PDF_TOOLS:
            df = self._extract_data_from_pdf(uploaded_file)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        return df
    
    def _extract_data_from_pdf(self, pdf_file):
        """Extract data from PDF file"""
        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_file.getvalue())
            temp_pdf_path = temp_pdf.name
        
        try:
            # Try using tabula-py first (works best for structured tables)
            tables = tabula.read_pdf(temp_pdf_path, pages='all', multiple_tables=True, guess=True, lattice=True)
            
            if tables and len(tables) > 0:
                # If multiple tables, combine them if possible
                if len(tables) > 1:
                    first_columns = set(tables[0].columns)
                    all_same_structure = all(set(table.columns) == first_columns for table in tables)
                    
                    if all_same_structure:
                        # Concat all tables
                        combined_df = pd.concat(tables, ignore_index=True)
                        os.unlink(temp_pdf_path)  # Clean up temp file
                        return combined_df
                    else:
                        # Use the largest table
                        largest_table = max(tables, key=len)
                        os.unlink(temp_pdf_path)  # Clean up temp file
                        return largest_table
                else:
                    # Just one table found
                    os.unlink(temp_pdf_path)  # Clean up temp file
                    return tables[0]
            
            # If tabula fails, try pdfplumber
            all_tables = []
            with pdfplumber.open(temp_pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:  # Check if table has content and more than just headers
                            if table[0]:  # Make sure there's a header row
                                df = pd.DataFrame(table[1:], columns=table[0])
                                all_tables.append(df)
            
            if all_tables:
                # Try to find tables with similar structures to combine
                tables_by_col_count = {}
                for table in all_tables:
                    col_count = len(table.columns)
                    if col_count not in tables_by_col_count:
                        tables_by_col_count[col_count] = []
                    tables_by_col_count[col_count].append(table)
                
                # Find the column count with the most tables
                most_common_col_count = max(tables_by_col_count.keys(), 
                                           key=lambda k: len(tables_by_col_count[k]))
                
                # Combine tables with this column count
                combined_df = pd.concat(tables_by_col_count[most_common_col_count], ignore_index=True)
                os.unlink(temp_pdf_path)  # Clean up temp file
                return combined_df
            
            # Last resort: Extract all text
            text = ""
            with open(temp_pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            # Try to identify tabular data in the text
            lines = text.split('\n')
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            
            # Create a basic DataFrame from the text for manual inspection
            raw_df = pd.DataFrame({"raw_text": non_empty_lines})
            
            # Attempt to further process the raw text
            processed_df = self._process_raw_pdf_text(raw_df)
            os.unlink(temp_pdf_path)  # Clean up temp file
            return processed_df
            
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
            
            # Create a DataFrame with error information
            error_df = pd.DataFrame({"Error": [f"Failed to extract data from PDF: {str(e)}"]})
            return error_df
    
    def _process_raw_pdf_text(self, df):
        """Process raw text extracted from PDFs"""
        # If this isn't raw text data, return as is
        if 'raw_text' not in df.columns or len(df.columns) > 1:
            return df
            
        text_lines = df['raw_text'].tolist()
        
        # Look for header row - often contains keywords like ID, Name, Premium, etc.
        header_candidates = []
        for i, line in enumerate(text_lines[:20]):  # Check first 20 lines
            # Convert to lowercase for case-insensitive matching
            line_lower = line.lower()
            # Check for common header terms
            header_terms = ['id', 'policy', 'member', 'product', 'plan', 'premium', 'commission']
            if sum(term in line_lower for term in header_terms) >= 2:
                header_candidates.append((i, line))
        
        if not header_candidates:
            # No clear header found, try to infer structure
            return self._infer_structure_from_raw_text(text_lines)
        
        # Use the best header candidate (most likely the one with most header terms)
        header_idx, header_line = max(
            header_candidates, 
            key=lambda x: sum(term in x[1].lower() for term in ['id', 'policy', 'member', 'product', 'premium'])
        )
        
        # Extract header column names
        # Try various ways to split the header
        potential_delimiters = ['\t', '  ', '|', ',', ';']
        best_split = None
        best_delimiter = None
        
        for delimiter in potential_delimiters:
            split = [col.strip() for col in header_line.split(delimiter) if col.strip()]
            if len(split) > 0 and (best_split is None or len(split) > len(best_split)):
                best_split = split
                best_delimiter = delimiter
        
        if best_split is None:
            # Still no clear delimiter, try to break by variable spacing
            best_split = [col.strip() for col in re.split(r'\s{2,}', header_line) if col.strip()]
            best_delimiter = r'\s{2,}'
        
        # Process the remaining lines using the same delimiter
        data_rows = []
        for line in text_lines[header_idx+1:]:
            if best_delimiter == r'\s{2,}':
                # Use regex for variable spacing
                row = [col.strip() for col in re.split(best_delimiter, line) if col.strip()]
            else:
                # Use the identified delimiter
                row = [col.strip() for col in line.split(best_delimiter) if col.strip()]
            
            # Only include rows that might have data (similar length to header)
            if row and len(row) >= len(best_split) - 1:
                # If row has more columns than headers, combine extras
                if len(row) > len(best_split):
                    row = row[:len(best_split)-1] + [' '.join(row[len(best_split)-1:])]
                # If row has fewer columns, pad with None
                elif len(row) < len(best_split):
                    row = row + [None] * (len(best_split) - len(row))
                data_rows.append(row)
        
        # Create DataFrame with the structured data
        result_df = pd.DataFrame(data_rows, columns=best_split)
        
        # Clean up the data, remove any rows that are likely page numbers or artifacts
        result_df = result_df[result_df.iloc[:, 0].astype(str).str.len() > 1]
        
        return result_df
    
    def _infer_structure_from_raw_text(self, text_lines):
        """Try to infer structure from unstructured PDF text"""
        # Filter out very short lines (likely artifacts)
        clean_lines = [line for line in text_lines if len(line) > 10]
        
        # Check if there's a pattern of numbers that might be policy IDs
        policy_pattern = re.compile(r'(\d{5,12})')  # 5-12 digit numbers common for policy IDs
        
        policy_lines = []
        for line in clean_lines:
            if policy_pattern.search(line):
                policy_lines.append(line)
        
        if policy_lines:
            # Try to extract structured data from these lines
            data = []
            for line in policy_lines:
                # Extract policy ID
                policy_match = policy_pattern.search(line)
                if policy_match:
                    policy_id = policy_match.group(1)
                    # Remove the policy ID from line to process the rest
                    rest = line[:policy_match.start()] + line[policy_match.end():]
                    
                    # Look for monetary amounts (premiums)
                    amount_pattern = re.compile(r'\$?(\d{1,3}(,\d{3})*(\.\d{2})?)')
                    amount_match = amount_pattern.search(rest)
                    premium = amount_match.group(1).replace(',', '') if amount_match else None
                    
                    # Try to identify product/plan
                    # This is challenging as product names vary widely
                    # Look for common product terms
                    product_terms = ['accident', 'critical', 'illness', 'hospital', 'cancer', 
                                    'disability', 'life', 'dental', 'vision']
                    
                    product = None
                    for term in product_terms:
                        if term.lower() in rest.lower():
                            # Extract a window around the term
                            term_idx = rest.lower().find(term.lower())
                            start = max(0, term_idx - 10)
                            end = min(len(rest), term_idx + len(term) + 15)
                            product = rest[start:end].strip()
                            break
                    
                    data.append({
                        'policy_id': policy_id,
                        'extracted_text': rest.strip(),
                        'product': product,
                        'premium': premium
                    })
            
            # Create DataFrame from extracted data
            return pd.DataFrame(data)
        
        # If no clear policy IDs found, return a DataFrame with the raw text for manual review
        return pd.DataFrame({'raw_text': text_lines})
    
    def identify_file_type(self, df):
        """Attempt to determine if file is enrollment report or invoice"""
        # Check column names to determine file type
        columns = [col.lower() for col in df.columns]
        
        # These are common columns expected in enrollment data
        enrollment_indicators = ['employee', 'member', 'insured', 'coverage', 'plan', 'policy', 'enrollee']
        
        # These are common columns expected in invoice data
        invoice_indicators = ['premium', 'commission', 'payment', 'invoice', 'billing', 'amount']
        
        enrollment_matches = sum(any(ind in col for col in columns) for ind in enrollment_indicators)
        invoice_matches = sum(any(ind in col for col in columns) for ind in invoice_indicators)
        
        if enrollment_matches > invoice_matches:
            return 'enrollment'
        else:
            return 'invoice'
    
    def standardize_data(self, df, file_type):
        """Standardize data from different sources into a common format"""
        # Create a copy to avoid modifying the original
        std_df = df.copy()
        
        # Convert all column names to lowercase and strip whitespace
        std_df.columns = [col.lower().strip() for col in std_df.columns]
        
        # If specific standardization logic is needed for different file formats, add it here
        if file_type == 'enrollment':
            # Standardize enrollment data
            
            # Look for employee/member ID column with various possible names
            id_columns = [col for col in std_df.columns if 
                         any(term in col for term in ['id', 'number', 'identifier', 'certificate'])]
            
            if id_columns:
                std_df.rename(columns={id_columns[0]: 'policy_id'}, inplace=True)
                
            # Look for product/plan/coverage column
            product_columns = [col for col in std_df.columns if
                              any(term in col for term in ['product', 'plan', 'coverage', 'benefit'])]
            
            if product_columns:
                std_df.rename(columns={product_columns[0]: 'product'}, inplace=True)
                
            # Look for premium/cost column
            premium_columns = [col for col in std_df.columns if
                              any(term in col for term in ['premium', 'cost', 'price', 'amount'])]
            
            if premium_columns:
                std_df.rename(columns={premium_columns[0]: 'premium'}, inplace=True)
                
            # Look for employee name columns
            name_columns = {}
            for col in std_df.columns:
                if any(term in col for term in ['first name', 'firstname', 'fname']):
                    name_columns['first_name'] = col
                elif any(term in col for term in ['last name', 'lastname', 'lname']):
                    name_columns['last_name'] = col
                elif any(term in col for term in ['name']) and 'first' not in col and 'last' not in col:
                    name_columns['full_name'] = col
            
            # Rename name columns if found
            for new_name, old_name in name_columns.items():
                std_df.rename(columns={old_name: new_name}, inplace=True)
                
            # If we have full_name but not first/last, try to split it
            if 'full_name' in std_df.columns and not ('first_name' in std_df.columns and 'last_name' in std_df.columns):
                # Try to split full name into first and last
                try:
                    std_df[['last_name', 'first_name']] = std_df['full_name'].str.split(',', 1, expand=True)
                except:
                    try:
                        std_df[['first_name', 'last_name']] = std_df['full_name'].str.split(n=1, expand=True)
                    except:
                        # If splitting fails, leave as is
                        pass
            
            # Look for SSN or last 4 digits of SSN
            ssn_columns = [col for col in std_df.columns if
                          any(term in col for term in ['ssn', 'social', 'security', 'tax'])]
            
            if ssn_columns:
                std_df.rename(columns={ssn_columns[0]: 'ssn'}, inplace=True)
                # Extract last 4 digits of SSN for matching purposes
                if 'ssn' in std_df.columns:
                    std_df['ssn_last4'] = std_df['ssn'].astype(str).str.replace(r'\D', '', regex=True).str[-4:]
                
        elif file_type == 'invoice':
            # Standardize invoice data
            
            # Look for policy ID column
            id_columns = [col for col in std_df.columns if 
                         any(term in col for term in ['policy', 'certificate', 'id', 'number', 'employee'])]
            
            if id_columns:
                std_df.rename(columns={id_columns[0]: 'policy_id'}, inplace=True)
                
            # Look for product/plan column
            product_columns = [col for col in std_df.columns if
                              any(term in col for term in ['product', 'plan', 'coverage', 'benefit', 'type'])]
            
            if product_columns:
                std_df.rename(columns={product_columns[0]: 'product'}, inplace=True)
                
            # Look for premium column
            premium_columns = [col for col in std_df.columns if
                              any(term in col for term in ['premium', 'amount', 'charge'])]
            
            if premium_columns:
                std_df.rename(columns={premium_columns[0]: 'premium'}, inplace=True)
                
            # Look for commission column
            commission_columns = [col for col in std_df.columns if
                                any(term in col for term in ['commission', 'comm', 'fee'])]
            
            if commission_columns:
                std_df.rename(columns={commission_columns[0]: 'commission'}, inplace=True)
                
            # Look for employee name columns - may be in format "Employee Name" or separate columns
            name_columns = {}
            for col in std_df.columns:
                if any(term in col for term in ['first name', 'firstname', 'fname']):
                    name_columns['first_name'] = col
                elif any(term in col for term in ['last name', 'lastname', 'lname']):
                    name_columns['last_name'] = col
                elif any(term in col for term in ['name', 'employee']) and 'product' not in col.lower():
                    name_columns['full_name'] = col
            
            # Rename name columns if found
            for new_name, old_name in name_columns.items():
                std_df.rename(columns={old_name: new_name}, inplace=True)
                
            # If we have full_name but not first/last, try to split it
            if 'full_name' in std_df.columns and not ('first_name' in std_df.columns and 'last_name' in std_df.columns):
                # Try to split full name into first and last
                try:
                    # Try comma format first (Last, First)
                    std_df[['last_name', 'first_name']] = std_df['full_name'].str.split(',', 1, expand=True)
                except:
                    try:
                        # Try space format (First Last)
                        std_df[['first_name', 'last_name']] = std_df['full_name'].str.split(n=1, expand=True)
                    except:
                        # If splitting fails, leave as is
                        pass
            
            # Look for SSN or last 4 digits of SSN
            ssn_columns = [col for col in std_df.columns if
                          any(term in col for term in ['ssn', 'social', 'security', 'tax', 'last 4'])]
            
            if ssn_columns:
                std_df.rename(columns={ssn_columns[0]: 'ssn'}, inplace=True)
                # Extract last 4 digits of SSN
                if 'ssn' in std_df.columns:
                    # Get only numeric characters and take last 4
                    std_df['ssn_last4'] = std_df['ssn'].astype(str).str.replace(r'\D', '', regex=True).str[-4:]
        
        # Ensure we have the minimum required columns, adding empty ones if needed
        required_columns = ['policy_id', 'product', 'premium']
        for col in required_columns:
            if col not in std_df.columns:
                std_df[col] = None
                
        # Convert premium to numeric, coercing errors to NaN
        if 'premium' in std_df.columns:
            # First clean the premium column - remove currency symbols and commas
            if std_df['premium'].dtype == 'object':
                std_df['premium'] = std_df['premium'].astype(str).str.replace(r'[$,]', '', regex=True)
            std_df['premium'] = pd.to_numeric(std_df['premium'], errors='coerce')
            
        return std_df
    
    def compare_enrollment_data(self, current_data, previous_data, matching_settings=None):
        """Compare current enrollment with previous data to identify new vs renewal policies"""
        # Apply matching settings if provided
        if matching_settings:
            self.use_policy_id_matching = matching_settings.get('use_policy_id', True)
            self.use_ssn_matching = matching_settings.get('use_ssn', True)
            self.use_name_matching = matching_settings.get('use_name', True)
            self.confidence_threshold = matching_settings.get('confidence_threshold', 0.7)
            self.fuzzy_threshold = matching_settings.get('fuzzy_threshold', 85)
        
        # Ensure both DataFrames have the required columns
        required_cols = ['policy_id', 'product', 'premium']
        for df in [current_data, previous_data]:
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns in data: {missing_cols}")
        
        # Create a copy of current data to add policy status
        result_df = current_data.copy()
        result_df['policy_status'] = 'new'  # Default all to new, then identify renewals
        result_df['match_confidence'] = 0.0  # Track confidence level of the match
        result_df['match_method'] = 'none'  # Track which method was used for matching
        
        # Step 1: Try matching on policy_id and product (exact match)
        if self.use_policy_id_matching:
            self._match_on_policy_id(result_df, previous_data)
        
        # Step 2: For unmatched policies, try matching on SSN (last 4) and product if available
        if self.use_ssn_matching and 'ssn_last4' in result_df.columns and 'ssn_last4' in previous_data.columns:
            mask = (result_df['policy_status'] == 'new') | (result_df['match_confidence'] < self.confidence_threshold)
            unmatched = result_df[mask].copy()
            self._match_on_ssn_last4(unmatched, previous_data)
            
            # Update the original DataFrame with matches from unmatched
            for idx, row in unmatched.iterrows():
                if row['match_confidence'] >= self.confidence_threshold:
                    result_df.loc[idx, 'policy_status'] = row['policy_status']
                    result_df.loc[idx, 'match_confidence'] = row['match_confidence']
                    result_df.loc[idx, 'match_method'] = row['match_method']
