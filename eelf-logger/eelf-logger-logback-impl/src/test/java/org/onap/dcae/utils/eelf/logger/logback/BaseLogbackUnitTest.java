/*
 * ================================================================================
 * Copyright (c) 2017 AT&T Intellectual Property. All rights reserved.
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
 * ECOMP is a trademark and service mark of AT&T Intellectual Property.
 */

package org.onap.dcae.utils.eelf.logger.logback;


import org.onap.dcae.utils.eelf.logger.api.info.CodeLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.CustomFieldsLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.ErrorLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.MessageLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.MiscLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.NagiosAlertLevel;
import org.onap.dcae.utils.eelf.logger.api.info.RequestIdLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.RequestStatusCode;
import org.onap.dcae.utils.eelf.logger.api.info.RequestTimingLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.ResponseLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.ServiceLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.TargetServiceLogInfo;
import org.onap.dcae.utils.eelf.logger.api.spec.AuditLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.DebugLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.ErrorLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.MetricLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;
import org.onap.dcae.utils.eelf.logger.model.info.CodeLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.CustomFieldsLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.ErrorLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.MessageLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.MiscLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.RequestIdLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.RequestTimingLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.ResponseLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.ServiceLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.TargetServiceLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.AuditLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.DebugLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.ErrorLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.MetricLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.OptionalLogSpecImpl;

import java.util.Date;

/**
 * Base Logback Unit Test.
 *
 * @author Rajiv Singla
 */
public abstract class BaseLogbackUnitTest {

    protected static final String TEST_SERVICE_INSTANCE_ID = "testServiceInstanceID";
    protected static final String TEST_INSTANCE_UUID = "";

    static {
        System.setProperty("ServiceInstanceId", TEST_SERVICE_INSTANCE_ID);
        System.setProperty("InstanceUUID", TEST_INSTANCE_UUID);
    }

    protected static final String TEST_REQUEST_ID = "403cdad8-4de7-450d-b441-561001decdd6";
    protected static final String TEST_SERVICE_NAME = "testServiceName";
    protected static final String TEST_PARTNER_NAME = "testPartnerName";
    protected static final String TEST_CLIENT_IP_ADDRESS = "";

    protected static final Date START_DATE = new Date();
    protected static final Date END_DATE = new Date(new Date().getTime() + 30_000);
    protected static final Long ELAPSED_TIME = END_DATE.getTime() - START_DATE.getTime();

    protected static final Integer RESPONSE_CODE = 200;
    protected static final String RESPONSE_DESCRIPTION = "TEST RESPONSE DESCRIPTION";

    protected static final String TEST_TARGET_ENTITY = "testTargetEntity";
    protected static final String TEST_TARGET_SERVICE_NAME = "testTargetServiceName";
    protected static final String TEST_TARGET_VIRTUAL_ENTITY = "testTargetVirtualEntity";


    protected static final String TEST_THREAD_ID = "testThreadId";
    protected static final String TEST_CLASS_NAME = "testClassName";

    protected static final String TEST_CUSTOM_FIELD1 = "testCustomField1";
    protected static final String TEST_CUSTOM_FIELD2 = "testCustomField2";
    protected static final String TEST_CUSTOM_FIELD3 = "testCustomField3";
    protected static final String TEST_CUSTOM_FIELD4 = "testCustomField4";

    protected static final String TEST_PROCESS_KEY = "testProcessId";

    protected static final Integer TEST_ERROR_CODE = 500;
    protected static final String TEST_ERROR_CODE_DESCRIPTION = "TEST ERROR CODE DESCRIPTION";


    protected static RequestIdLogInfo getTestRequestIdLogInfo() {
        return new RequestIdLogInfoImpl(TEST_REQUEST_ID);
    }

    protected static ServiceLogInfo getTestServiceLogInfo() {
        return new ServiceLogInfoImpl(TEST_SERVICE_NAME, TEST_PARTNER_NAME, TEST_CLIENT_IP_ADDRESS);
    }

    protected static RequestTimingLogInfo getTestRequestTimingInfo() {
        return new RequestTimingLogInfoImpl(START_DATE, END_DATE, ELAPSED_TIME);
    }

    protected static ResponseLogInfo getTestResponseLogInfo() {
        return new ResponseLogInfoImpl(RESPONSE_CODE, RESPONSE_DESCRIPTION);
    }

    protected static AuditLogSpec getTestAuditLogSpec() {
        return new AuditLogSpecImpl(getTestRequestIdLogInfo(), getTestServiceLogInfo(),
                getTestRequestTimingInfo(), getTestResponseLogInfo());
    }

    protected static DebugLogSpec getTestDebugLogSpec() {
        return new DebugLogSpecImpl(getTestRequestIdLogInfo());
    }

    protected static TargetServiceLogInfo getTestTargetServiceLogInfo() {
        return new TargetServiceLogInfoImpl(TEST_TARGET_ENTITY, TEST_TARGET_SERVICE_NAME, TEST_TARGET_VIRTUAL_ENTITY);
    }

    protected static MetricLogSpec getTestMetricLogSpec() {
        return new MetricLogSpecImpl(getTestRequestIdLogInfo(), getTestServiceLogInfo(),
                getTestRequestTimingInfo(), getTestResponseLogInfo(), getTestTargetServiceLogInfo());
    }

    protected static ErrorLogInfo getTestErrorLogInfo() {
        return new ErrorLogInfoImpl(TEST_ERROR_CODE, TEST_ERROR_CODE_DESCRIPTION);
    }

    protected static ErrorLogSpec getTestErrorLogSpec() {
        return new ErrorLogSpecImpl(getTestRequestIdLogInfo(), getTestServiceLogInfo(), getTestTargetServiceLogInfo()
                , getTestErrorLogInfo());
    }

    protected static OptionalLogSpec getTestOptionalLogSpec() {
        final MessageLogInfo messageLogInfo = new MessageLogInfoImpl(new Date(), RequestStatusCode.COMPLETE,
                NagiosAlertLevel.OK);
        final CodeLogInfo codeLogInfo = new CodeLogInfoImpl(TEST_THREAD_ID, TEST_CLASS_NAME);
        final CustomFieldsLogInfo customFieldsLogInfo = new CustomFieldsLogInfoImpl(TEST_CUSTOM_FIELD1,
                TEST_CUSTOM_FIELD2, TEST_CUSTOM_FIELD3, TEST_CUSTOM_FIELD4);
        final MiscLogInfo miscLogInfo = new MiscLogInfoImpl(TEST_PROCESS_KEY, "");
        return new OptionalLogSpecImpl(messageLogInfo, codeLogInfo, customFieldsLogInfo, miscLogInfo);
    }

}
