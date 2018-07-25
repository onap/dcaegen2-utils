/*
 * ================================================================================
 * Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
 * ================================================================================
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============LICENSE_END=========================================================
 *
 */

package org.onap.dcae.utils.eelf.logger.logback.log;

import org.junit.Test;
import org.onap.dcae.utils.eelf.logger.api.log.EELFLogFactory;
import org.onap.dcae.utils.eelf.logger.api.log.EELFLogger;
import org.onap.dcae.utils.eelf.logger.api.spec.MetricLogSpec;
import org.onap.dcae.utils.eelf.logger.logback.BaseLogbackUnitTest;
import org.onap.dcae.utils.eelf.logger.logback.EELFLoggerDefaults;
import org.onap.dcae.utils.eelf.logger.model.spec.MetricLogSpecImpl;


/**
 * Tests for Metric Log implementation.
 *
 * @author Rajiv Singla
 */
public class MetricLogImplTest extends BaseLogbackUnitTest {

    private static final EELFLogger LOG = EELFLogFactory.getLogger(MetricLogImplTest.class);

    @Test
    public void metricLoggerTest() throws Exception {

        LOG.metricLog().info("test Metric info message: {}", getTestMetricLogSpec(), getTestOptionalLogSpec(),
                "infoArg");

        final MetricLogSpec emptyMetricLog = new MetricLogSpecImpl(null, null, null, null, null);

        LOG.metricLog().info("Test Empty Metric info message", emptyMetricLog,
                EELFLoggerDefaults.DEFAULT_OPTIONAL_LOG_SPEC);
    }

    @Test
    public void metricLoggerTestWithWarnLogLevel() throws Exception {
        LOG.metricLog().warn("test Metric warn message: {}", getTestMetricLogSpec(), getTestOptionalLogSpec(),
                "warnArg");

    }

    @Test
    public void metricLoggerTestWithErrorLogLevel() throws Exception {
        LOG.metricLog().warn("test Metric error message: {}", getTestMetricLogSpec(), getTestOptionalLogSpec(),
                "errorArg");


    }

}
