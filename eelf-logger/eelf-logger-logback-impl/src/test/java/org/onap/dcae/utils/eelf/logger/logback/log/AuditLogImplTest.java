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
import org.onap.dcae.utils.eelf.logger.api.spec.AuditLogSpec;
import org.onap.dcae.utils.eelf.logger.logback.BaseLogbackUnitTest;
import org.onap.dcae.utils.eelf.logger.logback.EELFLoggerDefaults;
import org.onap.dcae.utils.eelf.logger.model.spec.AuditLogSpecImpl;

/**
 * Tests for Audit log implementations.
 *
 * @author Rajiv Singla
 */
public class AuditLogImplTest extends BaseLogbackUnitTest {

    private static final EELFLogger LOG = EELFLogFactory.getLogger(AuditLogImplTest.class);

    @Test
    public void auditLoggerTest() throws Exception {

        LOG.auditLog().info("Test Audit info message: {}",
                getTestAuditLogSpec(), getTestOptionalLogSpec(), "infoArg");

        final AuditLogSpec emptyAuditLog = new AuditLogSpecImpl(null, null,
                null, null);

        LOG.auditLog().info("Test Empty Audit info message.", emptyAuditLog,
                EELFLoggerDefaults.DEFAULT_OPTIONAL_LOG_SPEC);

    }


    @Test
    public void auditLoggerTestWithWarnLogLevel() throws Exception {
        LOG.auditLog().warn("Test Audit warn message: {}",
                getTestAuditLogSpec(), getTestOptionalLogSpec(), "warnArg");
    }

    @Test
    public void auditLoggerTestWithErrorLogLevel() throws Exception {
        LOG.auditLog().error("Test Audit error message: {}",
                getTestAuditLogSpec(), getTestOptionalLogSpec(), "errorArg");

    }
}
